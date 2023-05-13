# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from re import L
from flask import jsonify, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import CreateNameForm, CreateWordForm, LoginForm, CreateAccountForm,ChangePasswordForm
from app.base.models import User,Names,Lexicon,ConfigsTable

from app.base.util import verify_pass

changes_in_names_lexicon = True
changes_in_lexicon = True

@blueprint.route('/')
def route_default():
    return redirect(url_for('base_blueprint.login'))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'accounts/login.html',
                                form=login_form)
    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        # Check usename exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Username already registered',
                                    success=False,
                                    form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'accounts/register.html', 
                                    msg='Email already registered', 
                                    success=False,
                                    form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template( 'accounts/register.html', 
                                msg='User created please <a href="/admin/login">login</a>', 
                                success=True,
                                form=create_account_form)

    else:
        return render_template( 'accounts/register.html', form=create_account_form)


@blueprint.route('/admin/edit', methods = ['POST', 'GET'])
@login_required
def edit_password_admin():
    try:
        changepwd_form = ChangePasswordForm(request.form)
        if 'save' in request.form:
            
            # read form data
            user = current_user
            print(user)

            new_password = request.form['password']
            user.set_password(new_password)

            db.session.add(user)
            db.session.commit()
            logout_user()
            return redirect(url_for('base_blueprint.login'))
            # return redirect(url_for('home_blueprint.index'))

        return render_template( 'accounts/change_pwd.html',form=changepwd_form)

    except Exception as e:
        return render_template('error500.html')
   

@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
@login_required
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

@blueprint.route('/lexicon')
@login_required
def lexicon_main_page():
    lexicon_data = db.session.query(Lexicon).all()
    return  render_template( 'page-lexicon.html',data=lexicon_data)



@blueprint.route('/names')
@login_required
def names_main_page():
    names_data = db.session.query(Names).all()
    return  render_template( 'page-names.html',data=names_data)

@blueprint.route('/names/delete/<id>')
@login_required
def delete_name(id):
    global changes_in_names_lexicon
    name_data = db.session.query(Names).get(id)
    db.session.delete(name_data)
    db.session.commit()
    changes_in_names_lexicon = True
    
    default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_names').first()
    default_config.value = 'True'
    db.session.add(default_config)
    db.session.commit()
    return redirect(url_for('base_blueprint.names_main_page'))


@blueprint.route('/words/delete/<id>')
@login_required
def delete_word(id):
    global changes_in_lexicon
    word_data = db.session.query(Lexicon).get(id)
    db.session.delete(word_data)
    db.session.commit()
    changes_in_lexicon = True

    default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_lexicon').first()
    default_config.value = 'True'
    db.session.add(default_config)
    db.session.commit()
    return redirect(url_for('base_blueprint.lexicon_main_page'))


@blueprint.route('/addname', methods=['GET', 'POST'])
@login_required
def add_name():
    global changes_in_names_lexicon

    create_name_form = CreateNameForm(request.form)
    if 'add' in request.form:

        name  = request.form['name']
        gender     = request.form['gender']

        # Check usename exists
        name_obj = db.session.query(Names).filter_by(name=name).first()
        if name_obj is None:
            name_obj = Names()
            name_obj.name = name
            name_obj.gender = gender


            db.session.add(name_obj)
            db.session.commit()
            changes_in_names_lexicon = True

            default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_names').first()
            default_config.value = 'True'
            db.session.add(default_config)
            db.session.commit()
        
        return redirect(url_for('base_blueprint.names_main_page'))

    else:
        return render_template( 'addname.html', form=create_name_form)

@blueprint.route('/addword', methods=['GET', 'POST'])
@login_required
def add_word():
    global changes_in_lexicon
    create_word_form = CreateWordForm(request.form)
    if 'add' in request.form:
        from app.home.tweets_analysis_package.utils import clean_text
        word  = request.form['word']
        sentiment  = request.form['sentiment']
        
        # Check usename exists
        word_obj = db.session.query(Lexicon).filter_by(word=word).first()
        if word_obj is None:
            word_obj = Lexicon()
            word_obj.word = word
            word_obj.clean_word = clean_text(word)
            word_obj.sentiment = sentiment

            print(word_obj.clean_word )
            db.session.add(word_obj)
            db.session.commit()
        
            changes_in_lexicon = True
            default_config = db.session.query(ConfigsTable).filter_by(name='changes_in_lexicon').first()
            default_config.value = 'True'
            db.session.add(default_config)
            db.session.commit()

        return redirect(url_for('base_blueprint.lexicon_main_page'))

    else:
        return render_template( 'addword.html', form=create_word_form)

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('page-404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500
