
from datetime import datetime
from app.home.tweets_analysis_package.Gettweets import *
from app.home.models import History,db
import json
from app import celery,states,mail
from flask_mail import Message
from flask import current_app


@celery.task(bind=True)
def fetch_analyse_task(self, report_obj,country_name=None):
    self.update_state(state=states.PENDING)

    date_time_obj = datetime.datetime.strptime(report_obj['query_date'], '%Y-%m-%d')
    date_time_obj = date_time_obj.date()

    until_date = date_time_obj + datetime.timedelta(days=1)

    
    report_row = db.session.query(History).filter_by(query_date = date_time_obj,
                                                    query = report_obj['query'],
                                                    email = report_obj['email']).first()
    
    if report_row is not None and report_row.report is None:

        
        print(str(until_date))
        limit_tweet_count = None
        if country_name == None or country_name == 'None' or country_name == '0':
            country_name = None
        else:
            country_name = alpha2countries_dict[country_name][0]
            
        report = analyse_query( report_obj['timestamp'], report_obj['query'],
                                str(date_time_obj), str(until_date),
                                limit_tweet_count,country_name)

    
        report_row.report = json.dumps(report, default=np_encoder)
        db.session.add(report_row)
        db.session.commit()


    msg = Message('Tweets-Report Finished', recipients=[report_row.email])
    print(current_app.config['IP_ADDRESS'])
    ip_address = current_app.config['IP_ADDRESS']
    
    msg.html = f"""
    <html dir="rtl"> <head></head><body>
    <h3> مرحباً</h3> <br>
    <h3>
    لقد تم الانتهاء من عملية توليد التقرير التالي

    </h3>
    <br>
    <h3>
    كلمة البحث هي
    {report_row.query} 
    </h3>
    <br>
    <h3>
    التاريخ المراد البحث فيه هو
    {report_row.query_date} 
    </h3>
    <br>
    <h3>
    يمكنك الآن مشاهدة نتائج التقرير عبر الضغط على الرابط التالي
    </h3>
    <br>
    <h3>
    <a href="{ip_address}home?id={report_row.task_id}"> رابط التقرير</a>
    </h3>
    <br>
    <h3>
    وشكراً
    </h3>
    </body> </html> 
    """

    mail.send(msg)

    