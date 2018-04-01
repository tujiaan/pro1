# import datetime
#
# from app.ext import db
# from app.models import AskOrder
#
#
# def delete_order(app):
#     with app.app_context():
#         now = datetime.datetime.now()
#         yestoday = now - datetime.timedelta(days=1)
#         o = AskOrder.query.filter(AskOrder.state.in_([0, 1])).filter(AskOrder.create_time < yestoday).all()
#         for i in o:
#             if i.pay:
#                 db.session.delete(i.pay)
#             db.session.delete(i)
#             db.session.commit()
import datetime

import requests
from flask import app

from app.ext import db
from app.models import Sensor

def sendMessage(url):
    headers = {
        'FromAgent': 'third',
        'appKey': 'cfjbmqCwh50dShvDGhytug==',
        'appSecret': '9r2OQ+Z2j6QDdupm1mo8yQ=='
    }
    data = {
        'switch': [True]
    }
    r=requests.post(url, headers=headers,data=data)
    return None,200
def sendMessage2(url):
    headers = {
        'FromAgent': 'third',
        'appKey': 'cfjbmqCwh50dShvDGhytug==',
        'appSecret': '9r2OQ+Z2j6QDdupm1mo8yQ=='
    }
    data = {
        'switch': [False]
    }
    r=requests.post(url, headers=headers,data=data)
    return None,200







def test(app):
    with app.app_context():
        sensor=Sensor.query.all()
        url=''
        for i in sensor:
          if i.sensor_switch==True:
             time=datetime.datetime.now()
             if i.start_time==time:
                sendMessage(url)
             else:pass
             if i.end_time==time:
                sendMessage2(url)
                i.sensor_switch=False
                db.session.commit()
             else:pass
          else:pass





