# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String

from app import db, login_manager

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)
    
    def set_password(self,new_pass):
        value = hash_pass( new_pass )
        self.password = value


    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class Lexicon(db.Model):

    __tablename__ = 'lexicon'

    id = Column(Integer, primary_key=True)
    word = Column(String)
    clean_word = Column(String)
    sentiment = Column(String)
    
    def __repr__(self):
        return str(self.id)


    @property
    def serialize(self):
       return {
           'id'         : self.id,
           'word'         : self.word,
           'clean_word'         : self.clean_word,
           'sentiment'         : self.sentiment
       }
 
class Names(db.Model):

    __tablename__ = 'names'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    gender = Column(String)
    
    def __repr__(self):
        return str(self.id)


    @property
    def serialize(self):
       return {
           'id'         : self.id,
           'name'         : self.name,
           'gender'         : self.gender
       }
 
class ConfigsTable(db.Model):

    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    value = Column(String)
    
    def __repr__(self):
        return str(self.id)


    @property
    def serialize(self):
       return {
           'id'         : self.id,
           'name'         : self.name,
           'value'         : self.value
       }
 
