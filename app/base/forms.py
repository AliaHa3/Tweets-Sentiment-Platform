# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField,SelectField
from wtforms.validators import InputRequired, Email, DataRequired

## login and registration

class LoginForm(FlaskForm):
    username = TextField    ('Username', id='username_login'   , validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login'        , validators=[DataRequired()])


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Password', id='new_pwd'        , validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextField('Username'     , id='username_create' , validators=[DataRequired()])
    email    = TextField('Email'        , id='email_create'    , validators=[DataRequired(), Email()])
    password = PasswordField('Password' , id='pwd_create'      , validators=[DataRequired()])

class CreateWordForm(FlaskForm):
    word = TextField('الكلمة'     , id='word_create' , validators=[DataRequired()])
    sentiment = SelectField(u'التصنيف',
                            choices=[('pos', 'إيجابية'), ('neg', 'سلبية')],
                            validators=[DataRequired()])

class CreateNameForm(FlaskForm):
    name = TextField('الاسم'     , id='name_create' , validators=[DataRequired()])
    gender  =   SelectField(u'التصنيف',
                            choices=[('ذكر', 'ذكر'), ('انثى', 'انثى')],
                            validators=[DataRequired()])