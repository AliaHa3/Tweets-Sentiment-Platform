# -*- encoding: utf-8 -*-


import re

from flask.globals import request
from app.home import blueprint
from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from app import login_manager,db
from jinja2 import TemplateNotFound
from app.home.models import History
import json
import pandas as pd
import datetime


from app.home.worker_queue import celery,fetch_analyse_task,alpha2countries_dict

empty_report = {
    'total_tweet':
    1,
    'total_retweet':
    0,
    'total_likes':
    0,
    'total_tweets_per_hour':
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'total_retweets_per_hour':
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'total_likes_per_hour': [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0
    ],
    'most_liked_tweet':
    '',
    'most_retweet_tweet':
    '',
    'most_active_tweet':
    '',
    'total_published':
    0,
    'total_actions':
    0,
    'total_published_per_hour':
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'total_actions_per_hour': [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,0
    ],
    'lowest_active_hour':
    '',
    'highest_active_hour':
    '',
    'top_hashtags': [],
    'total_hashtags_count':
    0,
    'top_mentions': [],
    'total_mention_count':
    0,
    'top_countries_mentions': [],
    'top_countries_mentions_count':
    0,
    'analyse_sentiments': {
        'neg': 0,
        'neutral': 0,
        'pos': 0
    },
    'analyse_sources': {
        'Twitter Web Client': 0,
        'Twitter Web App': 0,
        'Twitter for Android': 0,
        'Twitter for iPhone': 0
    },
    'analyse_genders': {
        'unknown': 0,
        'male': 0,
        'female': 0
    }
}


allcountries = pd.read_csv('resources/countries_orginal.csv',encoding='utf8')
allcountries = list(allcountries.itertuples(index=False, name=None))

def check_report_data(report):
    fields = ['analyse_sentiments','analyse_sources','analyse_genders']
    for field in fields:
        for key,value in empty_report[field].items():
            if key not in report[field]:
                report[field][key] = value
    return report
        



@blueprint.route('/report', methods=['GET','POST'])
def report_request():
    try:
        yesterday = datetime.datetime.now() - datetime.timedelta(1)
        yesterday = yesterday.date()

        if request.method == 'POST':
            similar_report = db.session.query(History).filter_by ( query=request.form['hf-query'],
                                            query_date =  request.form['hf-date'] ).first()
            print(similar_report)
            if similar_report is None:
                new_report = History()
                new_report.query = request.form['hf-query']

                date_time_obj = datetime.datetime.strptime(request.form['hf-date'], '%Y-%m-%d')
                new_report.query_date = date_time_obj.date()
                new_report.email = request.form['hf-email']

                current_timestamp = int(datetime.datetime.now().timestamp())
                new_report.timestamp = str(current_timestamp)
                dict_report = new_report.serialize
                dict_report['query_date'] = request.form['hf-date']
                country = request.form['hf-country'] if request.form['hf-country'] else None
                print("tt")
                print(country)
                new_task = fetch_analyse_task.apply_async(args=[dict_report,country])
                task_id = new_task.task_id

                new_report.task_id = task_id
                
                print(new_report.task_id)

                db.session.add(new_report)
                db.session.commit()
            else:
                new_report = History()
                new_report.query = request.form['hf-query']
                date_time_obj = datetime.datetime.strptime(request.form['hf-date'], '%Y-%m-%d')
                new_report.query_date = date_time_obj.date()

                new_report.email = request.form['hf-email']

                current_timestamp = int(datetime.datetime.now().timestamp())
                new_report.timestamp = str(current_timestamp)
                dict_report = new_report.serialize
                dict_report['query_date'] = request.form['hf-date']
                
                new_report.task_id = similar_report.task_id
                new_report.report = similar_report.report

                db.session.add(new_report)
                db.session.commit()
                
                new_task = fetch_analyse_task.apply_async(args=[dict_report])

            
            return render_template('report_request.html',
                                    task_id = new_report.task_id,
                                    yesterday=yesterday,
                                    countries = allcountries)
        
        
        return render_template('report_request.html',
                                task_id = '',
                                yesterday=yesterday,
                                countries=allcountries)
    except Exception as e:
        print(e)

        return render_template('page-500.html'), 500

@blueprint.route('/home', methods=['GET','POST'])
def index():
    try:
        report = empty_report
        msg = None
        if request.method == 'POST':
            task_id = request.form['hf-reportid']
            similar_report = db.session.query(History).filter_by (task_id=task_id).first()
            if similar_report is None:
                report = empty_report
                msg = 'معرّف التقرير هذا غير موجود مسبقاً .. يرجى إنشاء تقرير جديد'
            elif similar_report.report is None:
                report = empty_report
                msg = 'لم يتم الانتهاء من عملية توليد التقرير بعد .. يرجى منك المحاولة لاحقاً'
            else:
                report = json.loads(similar_report.report)
                report = check_report_data(report)
                print(report)
            return render_template('index.html',msg=msg,report=report)
        elif 'id' in request.args:
            task_id = request.args['id']
            similar_report = db.session.query(History).filter_by (task_id=task_id).first()
            if similar_report is None:
                report = empty_report
                msg = 'معرّف التقرير هذا غير موجود مسبقاً .. يرجى إنشاء تقرير جديد'
            elif similar_report.report is None:
                report = empty_report
                msg = 'لم يتم الانتهاء من عملية توليد التقرير بعد .. يرجى منك المحاولة لاحقاً'
            else:
                report = json.loads(similar_report.report)
                report = check_report_data(report)
                print(report)
            return render_template('index.html',msg=msg,report=report)

        return render_template('index.html',report=report)
    except Exception as e:
        print(e)

        return render_template('page-500.html'), 500

@blueprint.route('/<template>')
def route_template(template):

    try:

        if not template.endswith( '.html' ):
            template += '.html'

        return render_template( template )

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500
