from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_trivia import Base, User, Question, Answer, Category, QuestionCategoryMap


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
            print "categories: " + str(i)
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
