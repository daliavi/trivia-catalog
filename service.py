from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_trivia import Base, User, Question, Answer, Category, question_category_association


def get_db_session():
    engine = create_engine('sqlite:///trivia_database.db')
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    return Session()

db_session = get_db_session()


def create_user(login_session):
    new_user = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def get_user_info(user_id):
    user = db_session.query(User).filter_by(id = user_id).one()
    return user


def get_user_by_email(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user
    except:
        return None


def get_user_id(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def user_picture_update(user_id, filepath):
    try:
        user = db_session.query(User).filter_by(id=user_id).one()
        user.picture = filepath
        db_session.add(user)
        db_session.commit()
    except:
        return None


def get_all_users():
    try:
        all_users = db_session.query(User).all()
        return all_users
    except:
        return None


def get_all_questions():
    try:
        all_questions = db_session.query(Question).all()
        return all_questions
    except:
        return None


def get_all_categories():
    try:
        all_categories = db_session.query(Category).all()
        return all_categories
    except:
        return None


def get_all_answers():
    all_answers = db_session.query(Answer).all()
    return all_answers


def get_questions_by_category(category_id):
    category = db_session.query(Category).filter_by(id=category_id).one()
    return category.questions


def get_question_by_id(question_id):
    question = db_session.query(Question).filter_by(id=question_id).one()
    return question


def answer_helper(q):
    r = q.serialize
    r.update({'Answers': [a.serialize for a in q.answers]})
    return r


def question_helper(c):
    r = c.serialize
    r.update({'Questions': [answer_helper(q) for q in c.questions]})
    return r


def get_all_data():
    categories = db_session.query(Category).all()
    category_list = [question_helper(c) for c in categories]
    return {'Categories': category_list}


def add_question(login_session, question, answers, categories):
    #get user id
    user = db_session.query(User).filter_by(email=login_session['email']).one()

    #save the question and return question ID
    question = Question(
        text=question,
        created_by=user.id
    )
    db_session.add(question)
    db_session.flush()

    if question.id:
        #save the answers
        answers = [
            Answer(
                text=answers[0][0],
                is_correct=answers[0][1],
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=answers[1][0],
                is_correct=answers[1][1],
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=answers[2][0],
                is_correct=answers[2][1],
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=answers[3][0],
                is_correct=answers[3][1],
                created_by=user.id,
                question_id=question.id
            )

        ]

        #assigning the question to category(ies)
        for i in categories:
            category = db_session.query(Category).filter_by(id=i).one()
            question.categories.append(category)
            db_session.add(question)

        db_session.bulk_save_objects(answers)  # NOTE!!! bulk operation needs sqlalchemy version 1.0 or higher
        db_session.commit()

        return question
    else:
        print "did not add the question"
        return None


def edit_question(user_email, question, answers, categories):
    error_msg = ''
    user_id = get_user_id(user_email)
    q = db_session.query(Question).filter_by(id=question[0]).one()
    if not q.created_by == user_id:
        error_msg = "The question could not be updated"
        return error_msg
    else:
        q.text = question[1]
        for a in answers:
            db_session.query(Answer).filter_by(id=a[0]).one().text = a[1]

        # updating categories of the question

        #get ids of the current categories
        cats_from_db = [c.id for c in q.categories]

        # ids of the new categories come in a list of strings, need to convert to int
        cats_new = map(int, categories)

        # finding category ids in either current or new list, but not in both
        cats_to_update = set(cats_from_db) ^ set(cats_new)

        # creating lists of category ids to remove and to add
        cats_to_remove = [c for c in cats_to_update if (c in cats_from_db)]
        cats_to_add = [c for c in cats_to_update if (c in cats_new)]

        if cats_to_remove:
            for i in cats_to_remove:
                print "in the loop: " + str(i)
                category = db_session.query(Category).filter_by(id=i).one()
                q.categories.remove(category)
                db_session.add(q)
        else:
            print "nothing to remove"

        if cats_to_add:
            # assigning new category(ies) to the question
            for i in cats_to_add:
                category = db_session.query(Category).filter_by(id=i).one()
                q.categories.append(category)
                db_session.add(q)
        else:
            print "nothing to add"

        db_session.commit()
        return error_msg


def add_category(login_session, category_name):
    # get user id
    user = db_session.query(User).filter_by(email=login_session['email']).one()

    # save the category
    category = Category(
        name=category_name,
        created_by=user.id,
    )
    db_session.add(category)
    db_session.commit()
    print "category id: " + str(category.id)
    return category


def delete_question(user_email, question_id):
    error_msg = ''
    user_id = get_user_id(user_email)
    question = db_session.query(Question).filter_by(id=question_id).one()
    if not question.created_by == user_id:
        error_msg = "The questions could not be deleted"
        return error_msg
    else:
        db_session.delete(question)
        db_session.commit()
        return error_msg


def delete_category(category_id):
    c = db_session.query(Category).filter_by(id=category_id).one()
    db_session.delete(c)
    db_session.commit()
    return
