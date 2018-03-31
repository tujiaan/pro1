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

from app.models import Sensor

def sendMessage():
   url=''
   data=None
   requests.post(url, data=data)







def test(app):
   sensor=Sensor.query.all()
   for i in sensor:
      if i.sensor_switch==True:
         time=datetime.datetime.now()
         if i.start_time==time:
            sendMessage()
         else:pass
         if i.end_time==time:
            sendMessage()
         else:pass
      else:pass





