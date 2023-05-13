# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from   decouple import config

class Config(object):

    basedir    = os.path.abspath(os.path.dirname(__file__))

    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='fjdslajfalshjdfjlasJDHJKS@&@!&@gwh()!')

    # This will create a file in <app> FOLDER
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'webdb.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
    # CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL= True
    MAIL_DEFAULT_SENDER = ''
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''

    IP_ADDRESS = ''



class DebugConfig(Config):
    DEBUG = True

# Load all possible configurations
config_dict = {
    'Debug'     : DebugConfig
}
