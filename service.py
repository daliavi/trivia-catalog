from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_trivia import Base, User, Question, Answer, Category, QuestionCategoryMap
from sqlalchemy import and_


def get_db_session():
    engine = create_engine('sqlite:///trivia_database.db')
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    return Session()

db_session = get_db_session()

def createUser(login_session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    db_session.add(newUser)
    db_session.commit()
    user = db_session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = db_session.query(User).filter_by(id = user_id).one()
    return user


def getUserID(email):
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_all_users():
    all_users = db_session.query(User).all()
    return all_users


def get_all_questions():
    all_questions = db_session.query(Question).all()
    return all_questions


def get_all_categories():
    all_categories = db_session.query(Category).all()
    return all_categories


def get_all_answers():
    all_answers = db_session.query(Answer).all()
    return all_answers


def get_all_mapping():
    all_mapping = db_session.query(QuestionCategoryMap).all()
    return all_mapping


def get_questions_by_category(category_id):
    questions = (db_session.query(Question)
                 .join(QuestionCategoryMap)
                 .filter(QuestionCategoryMap.category_id == category_id)
                 ).all()

    return questions


def get_question_by_id(question_id):
    question = db_session.query(Question).filter_by(id=question_id).one()
    return question


def get_all_data():
    answer_list = [
        {'id': '123', 'text': 'Vilnius', 'is_correct': 'True'},
        {'id': '123', 'text': 'Minsk', 'is_correct': 'False'},
        {'id': '123', 'text': 'Riga', 'is_correct': 'False'},
        {'id': '123', 'text': 'Talin', 'is_correct': 'False'},

    ]

    question_list = [
        {'id': '321', 'text': 'What is the capital of Lithuania_1?', 'created_by': '123', 'answers': answer_list},
        {'id': '321', 'text': 'What is the capital of Lithuania_2?', 'created_by': '123', 'answers': answer_list},
        {'id': '321', 'text': 'What is the capital of Lithuania_3?', 'created_by': '123', 'answers': answer_list},
    ]

    category_list = [
        {'id': '123', 'name': 'Biology', 'created_by': '321', 'questions': question_list},
        {'id': '123', 'name': 'History', 'created_by': '321', 'questions': question_list},
        {'id': '123', 'name': 'Maths', 'created_by': '321', 'questions': question_list},
    ]

    my_dict = {'categories': category_list}

    return my_dict


def add_question(login_session, question, correct_answer,
        alt_answer_1, alt_answer_2, alt_answer_3, categories):
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
                text=correct_answer,
                is_correct=True,
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=alt_answer_1,
                is_correct=False,
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=alt_answer_2,
                is_correct=False,
                created_by=user.id,
                question_id=question.id
            ),
            Answer(
                text=alt_answer_3,
                is_correct=False,
                created_by=user.id,
                question_id=question.id
            )

        ]
        question_categories = []

        for i in categories:
            question_categories.append(
                QuestionCategoryMap(
                    category_id=i,
                    question_id=question.id
                )
            )

        db_session.bulk_save_objects(answers)  # needs sqlalchemy version 1.0 or higher
        db_session.bulk_save_objects(question_categories)
        db_session.commit()

        return question
    else:
        print "did not add the question"
        return None


def edit_question(question, answers, categories):
    q = db_session.query(Question).filter_by(id=question[0]).one()
    q.text = question[1]

    for a in answers:
        db_session.query(Answer).filter_by(id=a[0]).one().text = a[1]

    # updating categories of the question
    cats_from_db = [c.category_id for c in db_session.query(QuestionCategoryMap.category_id).filter_by(
        question_id=question[0])]

    # new categories come in a list of strings, need to convert to int
    cats_new = map(int, categories)

    # finding categories in either current or new list, but not in both
    cats_to_update = set(cats_from_db) ^ set(cats_new)

    # creating lists of categories to remove and to add
    cats_to_remove = [c for c in cats_to_update if (c in cats_from_db)]
    cats_to_add = [c for c in cats_to_update if (c in cats_new)]

    if cats_to_remove:
        db_session.query(QuestionCategoryMap).filter(and_(
            QuestionCategoryMap.question_id == question[0],
            QuestionCategoryMap.category_id.in_(cats_to_remove)
            )).delete(synchronize_session='fetch')
    else:
        print "nothing to remove"

    if cats_to_add:
        new_question_categories = []
        for i in cats_to_add:
            new_question_categories.append(
                QuestionCategoryMap(
                    category_id=i,
                    question_id=question[0]
                )
            )
        db_session.bulk_save_objects(new_question_categories)
    else:
        print "nothing to add"

    db_session.commit()

    return


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


def delete_question(question_id):
    question = db_session.query(Question).filter_by(id=question_id).one()
    db_session.delete(question)
    db_session.commit()
    return
