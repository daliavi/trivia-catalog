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
