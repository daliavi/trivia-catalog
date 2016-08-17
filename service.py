from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_trivia import Base, User, Question, Answer, Category, QuestionCategoryMap
from sqlalchemy import and_


def get_db_session():
    engine = create_engine('sqlite:///trivia_database.db')
    Base.metadata.bind = engine
    Session = sessionmaker(bind=engine)
    return Session()


def createUser(login_session, session):
    newUser = User(
        name=login_session['username'],
        email=login_session['email'],
        picture=login_session['picture']
    )
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(session, user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user


def getUserID(session, email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def get_all_users(session):
    all_users = session.query(User).all()
    return all_users


def get_all_questions(session):
    all_questions = session.query(Question).all()
    return all_questions


def get_all_categories(session):
    all_categories = session.query(Category).all()
    return all_categories


def get_all_answers(session):
    all_answers = session.query(Answer).all()
    return all_answers


def get_all_mapping(session):
    all_mapping = session.query(QuestionCategoryMap).all()
    return all_mapping


def get_questions_by_category(session, category_id):
    questions = (session.query(Question)
                 .join(QuestionCategoryMap)
                 .filter(QuestionCategoryMap.category_id == category_id)
                 ).all()

    return questions


def get_question_by_id(session, question_id):
    question = session.query(Question).filter_by(id=question_id).one()
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


def add_question(
        session, login_session, question, correct_answer,
        alt_answer_1, alt_answer_2, alt_answer_3, categories):
    #get user id
    user = session.query(User).filter_by(email=login_session['email']).one()

    #save the question and return question ID
    question = Question(
        text=question,
        created_by=user.id
    )
    session.add(question)
    session.flush()

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

        session.bulk_save_objects(answers)  # needs sqlalchemy version 1.0 or higher
        session.bulk_save_objects(question_categories)
        session.commit()

        return question
    else:
        print "did not add the question"
        return None


def update_question(session, question_id, question_text, correct_answer, correct_answer_id,
                    alt_answer_1, alt_answer_1_id,
                    alt_answer_2, alt_answer_2_id,
                    alt_answer_3, alt_answer_3_id, categories):

    # updating the question
    question = session.query(Question).filter_by(id=question_id).one()
    question.text = question_text

    # updating the answers
    answer_correct = session.query(Answer).filter_by(id=correct_answer_id).one()
    answer_correct.text = correct_answer

    answer_alt_1 = session.query(Answer).filter_by(id=alt_answer_1_id).one()
    answer_alt_1.text = alt_answer_1

    answer_alt_2 = session.query(Answer).filter_by(id=alt_answer_2_id).one()
    answer_alt_2.text = alt_answer_2

    answer_alt_3 = session.query(Answer).filter_by(id=alt_answer_3_id).one()
    answer_alt_3.text = alt_answer_3

    # updating categories of the question
    current_cat = [u.category_id for u in session.query(QuestionCategoryMap.category_id).filter_by(
        question_id=question_id)]

    # new categories come in a list of strings, need to convert to int
    new_cat = map(int, categories)

    # finding categories in either current or new list, but not in both
    items = set(current_cat) ^ set(new_cat)

    # creating lists of categories to remove and to add
    cat_to_remove = [i for i in items if (i in current_cat)]
    cat_to_add = [i for i in items if (i in new_cat)]

    if cat_to_remove:
        session.query(QuestionCategoryMap).filter(and_(
            QuestionCategoryMap.question_id == question_id,
            QuestionCategoryMap.category_id.in_(cat_to_remove)
            )).delete(synchronize_session='fetch')
    else:
        print "nothing to remove"

    if cat_to_add:
        new_question_categories = []
        for i in cat_to_add:
            new_question_categories.append(
                QuestionCategoryMap(
                    category_id=i,
                    question_id=question.id
                )
            )
        session.bulk_save_objects(new_question_categories)
    else:
        print "nothing to add"

    session.commit()
    return


def add_category(session, login_session, category_name):
    # get user id
    user = session.query(User).filter_by(email=login_session['email']).one()

    # save the category
    category = Category(
        name=category_name,
        created_by=user.id,
    )
    session.add(category)
    session.commit()
    print "category id: " + str(category.id)
    return category


def delete_question(session, question_id):
    question = session.query(Question).filter_by(id=question_id).one()
    session.delete(question)
    session.commit()
    return
