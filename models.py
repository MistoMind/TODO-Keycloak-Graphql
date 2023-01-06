from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship,
                            backref)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///todoDB.sqlite3', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


class User(Base):
    __tablename__ = 'user'
    id = Column("user_id", Integer, primary_key=True)
    name = Column("name", String)
    password = Column("password", String)
    email = Column("email", String, unique=True)


class Todo(Base):
    __tablename__ = 'todo'
    todo_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(User.id))
    title = Column(String)
    description = Column(String)
    date_time = Column(DateTime)
