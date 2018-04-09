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

import math
from operator import or_

import requests
from flask import app

from app.ext import db
from app.models import Sensor, SensorAlarm, MessageSend, Home, HomeUser, User, Ins, UserAlarmRecord, Role, UserRole


def BuiltSensorSendMessage(app):
    with app.app_context():
        sensoralarm=SensorAlarm.query.all()
        for i in sensoralarm:
            if i.if_confirm==False:
                home=Home.query.filter(Home.gateway_id==sensoralarm.gateway_id).first()
                homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
                user=User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
                for i in user:
                    messagesend=MessageSend(message_id=sensoralarm.id,message_type='传感器报警',user_id=i.id)
                    db.session.add(messagesend)
                    db.session.commit()
                if i.is_timeout==True:
                    community=home.community
                    ins=[]
                    for i in community:
                        ins.extend(i.ins)
                    for i in ins:
                        for j in i.user:
                            messagesend = MessageSend(message_id=sensoralarm.id, message_type='传感器报警', user_id=j.id)
                            db.session.add(messagesend)
                            db.session.commit()
                else:pass
            else:pass
    return None, 200
def BuiltUserSendMessage(app):
    def getDistance(lat0, lng0, lat1, lng1):
        lat0 = math.radians(lat0)
        lat1 = math.radians(lat1)
        lng0 = math.radians(lng0)
        lng1 = math.radians(lng1)

        dlng = math.fabs(lng0 - lng1)
        dlat = math.fabs(lat0 - lat1)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat0) * math.cos(lat1) * math.sin(dlng / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # 地球平均半径，单位为公里
        return c * r * 1000
    with app.app_context():
        useralarmrecord=UserAlarmRecord.query.all()
        for i in useralarmrecord:
            home1 = Home.query.filter(Home.id == UserAlarmRecord.home_id)
            community = home1.community
            if i.if_confirm==False:
                home2=Home.query.filter(or_(getDistance(Home.latitude,Home.latitude,home1.latitude,home1.longitude)<community.eva_distance,getDistance(Home.latitude,Home.latitude,home1.latitude,home1.longitude)<community.save_distance))
                home=home1.union(home2).all()
                homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
                user=User.query.filter(User.id.in_(i.user_id for i in homeuser))
                for i in user:
                    messagesend=MessageSend(message_id=useralarmrecord.id,message_type='传感器报警',user_id=i.id)
                    db.session.add(messagesend)
                    db.session.commit()
            else:
                ins=[]
                for i in community:
                    ins.extend(i.ins)
                user1=[]
                for i in ins:
                    user1.extend(i.user)
                role=Role.query.filter(or_(Role.name=='admin',Role.name=='superadmin')).all()
                userrole=UserRole.filter(UserRole.role_id.in_(i.id for i in role)).all()
                user2=User.query.filter(User.id.in_(i.user_id for i in userrole)).all()
                user3=user2.extend(user1)
                for i in user3:######################
                    messagesend = MessageSend(message_id=useralarmrecord.id, message_type='传感器报警', user_id=i.id)
                    db.session.add(messagesend)
                    db.session.commit()
    return None,200
    # useralarmrecord = UserAlarmRecord.query.get_or_404(useralarmrecordid)
    # homeuser = HomeUser.query.filter(HomeUser.home_id == useralarmrecord.home_id).all()
    # user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
    # home = Home.query.get_or_404(useralarmrecord.home_id)
    # ins = home.community.ins
    # list1 = []
    # for i in ins:
    #     list1.append(i.user)
    # if useralarmrecord.type == 0 or useralarmrecord.type == 1:
    #     userrole = UserRole.query.filter(or_(UserRole.role_id == 4, UserRole.role_id == 5, UserRole.role_id == 6)).all()
    #     query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
    #     query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
    #     query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
    #
    # elif useralarmrecord.type == 2:
    #     query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
    #     query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
    #     userrole = UserRole.query.filter(or_(UserRole.role_id == 5, UserRole.role_id == 6)).all()
    #     query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
    #
    # else:
    #     query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
    #     query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
    #     userrole = UserRole.query.filter(or_(UserRole.role_id == 5, UserRole.role_id != 4, UserRole.role_id == 6)).all()
    #     query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
    # list2 = query1.union(query2).union(query3).all()
    #   for i in user3:
#            messagesend = MessageSend(message_id=useralarmrecord.id, message_type='传感器报警', user_id=i.id)
#            db.session.add(messagesend)
#            db.session.commit()
    #   return None,200
    #






