import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
# from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
import sqlalchemy as sa

Base = declarative_base()


question_category_association = sa.Table('QuestionCategoryAss', Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id')),
    Column('question_id', Integer, ForeignKey('question.id')))


class User(Base):
    __tablename__ = 'user'

    id = Column(
        Integer, primary_key=True
    )

    name = Column(
        String(250),
        nullable=False
    )

    email = Column(
        String(250),
        nullable=False
    )

    picture = Column(
        String(250)
    )

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
        }


class Question(Base):
    __tablename__ = 'question'

    id = Column(
        Integer, primary_key=True
    )

    text = Column(
        String(1024),
        nullable=False
    )

    created_by = Column(
        Integer, ForeignKey('user.id')
    )

    answers = relationship("Answer", backref="question", cascade="all, delete-orphan")

    # categories = relationship("QuestionCategoryMap", backref="question")

    categories = relationship(
        "Category",
        secondary=question_category_association,
        back_populates="questions")

    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'text': self.text,
            'created_by': self.created_by,
        }


class Answer(Base):
        __tablename__ = 'answer'

        id = Column(
            Integer, primary_key=True
        )

        text = Column(
            String(80),
            nullable=False
        )

        is_correct = Column(
            Boolean,
            default=False
        )

        created_by = Column(
            Integer, ForeignKey('user.id')
        )

        question_id = Column(
            Integer, ForeignKey('question.id')
        )

        user = relationship(User)

        @property
        def serialize(self):
            # Returns object data in easily serializeable format
            return {
                'id': self.id,
                'text': self.text,
                'is_correct': self.is_correct,
                'created_by': self.created_by,
                'question_id': self.question_id,
            }


class Category(Base):
    __tablename__ = 'category'

    name = Column(
        String(80),
        nullable=False
    )

    id = Column(
        Integer, primary_key=True
    )

    created_by = Column(
        Integer, ForeignKey('user.id')
    )

    user = relationship(User)

    questions = relationship(
        "Question",
        secondary=question_category_association,
        back_populates="categories")

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return{
            'id': self.id,
            'name':self.name,
            'created_by': self.created_by
        }


class QuestionCategoryMap(Base):
    __tablename__ = 'question_category_map'

    id = Column(
        Integer, primary_key=True
    )

    category_id = Column(
        Integer, ForeignKey('category.id')
    )

    question_id = Column(
        Integer, ForeignKey('question.id')
    )

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'category_id': self.category_id,
            'question_id': self.question_id
        }

## end of file
engine = create_engine('sqlite:///trivia_database.db')
Base.metadata.create_all(engine)