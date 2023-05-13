# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import Flask, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from logging import basicConfig, DEBUG, getLogger, StreamHandler
from os import path
from flask_mail import Mail, Message

db = SQLAlchemy()
mail= Mail()
login_manager = LoginManager()

from celery import Celery, states
celery =  Celery('tasks',broker='pyamqp://guest@localhost//')


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)

def register_blueprints(app):
    for module_name in ('base','home'): #base
        module = import_module('app.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)

def configure_database(app):

    @app.before_first_request
    def initialize_database():
        db.create_all()

        import pandas as pd
        from app.base.models import Names,Lexicon,User,ConfigsTable

        
        admin = db.session.query(User).filter_by(id=1)
        if admin is None:
            c = User(username='admin',email = 'admin@admin.com',password = '123456')
            db.session.add(c)
            db.session.commit()
        
        default_config = ConfigsTable()
        default_config.name = 'changes_in_lexicon'
        default_config.value = 'True'
        db.session.add(default_config)

        default_config = ConfigsTable()
        default_config.name = 'changes_in_names'
        default_config.value = 'True'
        db.session.add(default_config)
            
        # gender_names_lexicon = pd.read_csv('arabic_names_with_gender.csv',encoding='utf8')
        # lexicon = pd.read_csv('lexicon.csv',encoding='utf8')
        # add = True
        # for i,row in lexicon.iterrows():
        #     if add:
        #         _obj = Lexicon()
        #         _obj.word = row['word']
        #         _obj.clean_word = row['clean_word']
        #         _obj.sentiment = row['sentiment']
        #         db.session.add(_obj)
        #         db.session.commit()
        #         print(i)
        # add = False
            
    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()


    
def create_app(config):
    app = Flask(__name__, static_folder='base/static')
    app.config.from_object(config)
    with app.app_context():
        register_extensions(app)
        
        celery.conf.update(app.config)

        register_blueprints(app)
        configure_database(app)

        mail.init_app(app)

    return app
