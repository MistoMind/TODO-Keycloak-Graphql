from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship)
from sqlalchemy.ext.declarative import declarative_base
import os
import datetime

BASE_DIR = os.getcwd()
engine = create_engine(f'sqlite:///{BASE_DIR}/todoDB.db')
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base(bind=engine)
Base.query = session.query_property()


class Notes(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    body = Column(Text)
    time = Column(Time, default=None)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates="notes")


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100))
    password = Column(String(200))
    notes = relationship('Notes', back_populates="user")
