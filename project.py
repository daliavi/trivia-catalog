from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import service
import logging

#for oauth implementation:
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


CLIENT_ID = json.loads(
    open('client_secrets.json','r').read())['web']['client_id']

app = Flask(__name__)

session = service.get_db_session()


# registering custom filter for jinja
@app.template_filter('shuffle')
def reverse_filter(s):
    try:
        result = list(s)
        random.shuffle(result)
        return result
    except:
        return s

# creating anti-forgery state token
@app.route('/login')
def showLogin():
    login_session.clear()
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32)
    )
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = service.getUserID(session, login_session['email'])
    if not user_id:
        user_id = service.createUser(login_session, session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    login_session.clear()
    return "you have been logged out"



@app.route('/gconnect', methods=['POST'])
def gconnect():
    app.logger.info('Starting gconnect, Client id: %s' % CLIENT_ID)
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = service.getUserID(session=session, email=login_session['email'])
    if not user_id:
        user_id = service.createUser(login_session, session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        # del login_session['access_token']
        # del login_session['gplus_id']
        # del login_session['username']
        # del login_session['email']
        # del login_session['picture']
        # del login_session['user_id']
        login_session.clear()
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


#Test engpoint to return users
@app.route('/users/JSON')
def usersJSON():
    users = service.get_all_users(session=session)
    return jsonify(Users=[i.serialize for i in users])

#Test engpoint to return all questions
@app.route('/questions/JSON')
def questionsJSON():
    questions = service.get_all_questions(session=session)
    return jsonify(Questions=[i.serialize for i in questions])

#Test engpoint to return all categories
@app.route('/categories/JSON')
def categoriesJSON():
    categories = service.get_all_categories(session=session)
    return jsonify(Categories=[i.serialize for i in categories])

#Test engpoint to return all questions
@app.route('/answers/JSON')
def answersJSON():
    answers = service.get_all_answers(session=session)
    return jsonify(Answers=[i.serialize for i in answers])  # Test engpoint to return all questions

#Test engpoint to return all category-question mappings
@app.route('/mapping/JSON')
def categoryMappingJSON():
    mapping = service.get_all_mapping(session=session)
    return jsonify(Category_mapping=[i.serialize for i in mapping])

#Test engpoint to test
@app.route('/test/JSON')
def testJSON():
    my_dict = service.get_all_data()

    return jsonify(my_dict)


@app.route('/question/new/', methods=['GET', 'POST'])
def new_question():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        service.add_question(
            session=session,
            login_session=login_session,
            question=request.form['question'],
            correct_answer=request.form['correct_answer'],
            alt_answer_1=request.form['alt_answer_1'],
            alt_answer_2=request.form['alt_answer_2'],
            alt_answer_3=request.form['alt_answer_3'],
            categories=request.form.getlist('categories')
        )
        flash('New question created!')
        return redirect('/')
    else:  # if received GET
        categories = service.get_all_categories(session=session)
        return render_template('newquestion.html', categories=categories)


@app.route('/category/new/', methods=['GET', 'POST'])
def new_category():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        service.add_category(
            session=session,
            login_session=login_session,
            category_name=request.form['category_name']
        )
        flash('New category created!')
        return redirect('/')
    else:  # if received GET
        #TODO get category dictionary
        categories = {'biol': '1', 'hist':'2', 'astr':'5'}
        return render_template('newcategory.html', categories=categories)


@app.route('/', methods=['GET', 'POST'])
def main():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        pass
    else:  # if received GET
        # TODO get category dictionary
        # categories = {'biol': '1', 'hist': '2', 'astr': '5'}
        questions = service.get_all_questions(session=session)
        categories = service.get_all_categories(session=session)
        return render_template('main.html',
                               categories=categories, questions=questions)


#  how to build URL like /category/<int:category_id>/questions ???
@app.route('/category/<int:category_id>', methods=['GET', 'POST'])
def questions_by_category(category_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        pass
    else:  # if received GET
        questions = service.get_questions_by_category(
            session=session,
            category_id=category_id
        )
        answers = [question.answers for question in questions]
        categories = service.get_all_categories(session=session)
        print questions
        print answers
        return render_template('main.html',
                               categories=categories,
                               questions=questions,
                               answers=answers)


@app.route('/question/delete/<int:question_id>', methods=['GET', 'POST'])
def delete_question(question_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['submit'] == 'Delete':
            service.delete_question(
                session=session,
                question_id=question_id
            )
            flash('The question was deleted!')

        return redirect('/')

    else:  # if received GET
        question = service.get_question_by_id(
            session=session,
            question_id=question_id
        )
        return render_template('deletequestion.html',
                               question=question)


@app.route('/_category2python')
def array2python():
    category_id = json.loads(request.args.get('category_id'))
    # do some stuff
    print "Got from JS: " + str(category_id)
    return jsonify(result=category_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host = '0.0.0.0', port=5000)