
from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String,Text,Date

from app import db

from app.base.util import hash_pass

class History(db.Model):

    __tablename__ = 'history'

    id = Column(Integer, primary_key=True)
    query = Column(String)
    query_date = Column(Date)
    task_id = Column(Text)
    timestamp = Column(Text)
    email = Column(String)
    report = Column(Text)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

                
            setattr(self, property, value)

    def __repr__(self):
        return str(self.task_id)


    @property
    def serialize(self):
       return {
           'id'         : self.id,
           'query'         : self.query,
           'query_date'         : self.query_date,
           'task_id'         : self.task_id,
           'timestamp'         : self.timestamp,
           'report'         : self.report,
           'email'         : self.email
       }
 