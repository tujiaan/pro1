from operator import or_, and_

import requests
from flask import app

from app.ext import db, getui
from app.models import Sensor, SensorAlarm, MessageSend, Home, HomeUser, User, Ins, UserAlarmRecord, Role, UserRole


def BuiltSensorSendMessage(app):
    with app.app_context():
        sensoralarm=SensorAlarm.query.all()
        for i in sensoralarm:
            if i.is_confirm==False:
                home=Home.query.filter(Home.gateway_id==i.gateway_id).first()
                homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
                user=User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
                for j in user:
                    messagesend=MessageSend(message_id=i.id,message_type='传感器报警',user_id=j.id)
                    ms=MessageSend.query.filter(and_(MessageSend.message_id==i.id,MessageSend.user_id==j.id)).first()
                    if ms==None:
                        db.session.add(messagesend)
                        db.session.commit()
                    else:pass
                if i.is_timeout==True:
                    community=home.community
                    ins=community.ins
                    for j in ins:
                        for k in j.user:
                            messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=k.id)
                            ms = MessageSend.query.filter(
                                and_(MessageSend.message_id == i.id, MessageSend.user_id == j.id)).first()
                            if ms == None:
                                db.session.add(messagesend)
                                db.session.commit()
                            else:
                                pass
                else:pass
            else:pass
    return None, 200
def BuiltUserSendMessage(app):
    with app.app_context():
        useralarmrecord = UserAlarmRecord.query.all()
        print('1')
        for i in useralarmrecord:
            homeuser = HomeUser.query.filter(HomeUser.home_id == i.home_id).all()
            user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
            home = Home.query.get_or_404(i.home_id)
            ins = home.community.ins
            list1 = []
            for j in ins:
                list1.extend(j.user)
            if i.type == 0 or i.type == 1:
                ur1 = UserRole.query.filter(or_(UserRole.role_id=='4',UserRole.role_id=='5'))
                ur2=UserRole.query.filter(UserRole.role_id=='6')
                userrole=ur1.union(ur2).all()
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

            elif i.type == 2:
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

            else:
                ur1 = UserRole.query.filter(or_(UserRole.role_id == '4', UserRole.role_id == '5'))
                ur2 = UserRole.query.filter(UserRole.role_id == '6')
                userrole = ur1.union(ur2).all()
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
            list2 = query1.union(query2).union(query3).all()
            print(list2)
            print('2')
            for j in list2:
                   messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id)
                   ms=MessageSend.query.filter(and_(MessageSend.message_id==i.id,MessageSend.user_id==j.id)).first()
                   if ms==None:
                       db.session.add(messagesend)
                       db.session.commit()
                   else:pass
            return None,200


def SendMessage(app):
    with app.app_context():
        sensoralarm=SensorAlarm.query.all()
        for i in sensoralarm:
            messagesend=MessageSend.query.filter(MessageSend.message_id==i.id).all()
            list = []
            for i in messagesend:
                if i.message_type == '传感器报警':
                    sensoralarm = SensorAlarm.query.get_or_404(i.message_id)
                    if sensoralarm.sensor_type == '0':
                        content = '烟雾传感器' + sensoralarm.sensor_id + '异常'
                    elif sensoralarm.sensor_type == '1':
                        content = '温度传感器' + sensoralarm.sensor_id + '异常'
                    elif sensoralarm.sensor_type == '2':
                        content = '燃气阀' + sensoralarm.sensor_id + '异常'
                    elif sensoralarm.sensor_type == '3':
                        content = '智能插座' + sensoralarm.sensor_id + '异常'
                    else:content = '电磁阀' + sensoralarm.sensor_id + '异常'
                if i.if_send==False:
                    list.append(i.user_id)
                    i.if_send = True
                    db.session.commit()
                else:pass
            taskid=getui.getTaskId(content)
            getui.sendList(alias=list,taskid=taskid)













