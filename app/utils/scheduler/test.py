import datetime
from operator import or_, and_

import requests
from flask import app, json

from app.ext import db, getui,mqtt
from app.models import Sensor, SensorAlarm, MessageSend, Home, HomeUser, User, Ins, UserAlarmRecord, Role, UserRole, \
    SensorTime


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
        for i in useralarmrecord:
            homeuser = HomeUser.query.filter(HomeUser.home_id == useralarmrecord.home_id).all()
            user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
            home = Home.query.get_or_404(useralarmrecord.home_id)
            ins = home.community.ins
            list1 = []
            for i in ins:
                list1.append(i.user)
            if useralarmrecord.type == 0 or useralarmrecord.type == 1:
                userrole = UserRole.query.filter(UserRole.role_id.in_['4','5','6']).all()
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

            elif useralarmrecord.type == 2:
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

            else:
                query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
                query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
                userrole = UserRole.query.filter(UserRole.role_id.in_['4','5','6']).all()
                query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
            list2 = query1.union(query2).union(query3).all()
            for i in list2:
                   messagesend = MessageSend(message_id=useralarmrecord.id, message_type='用户报警', user_id=i.id)
                   db.session.add(messagesend)
                   db.session.commit()
            return None,200

def SendMessage(app):
    with app.app_context():
        sendmessage=MessageSend.query.filter(MessageSend.if_send==False).order_by(MessageSend.message_id).all()
        for i in sendmessage:
            if i.message_type=='传感器报警':
                sensoralarm=SensorAlarm.query.get_or_404(i.message_id)
                if sensoralarm.sensor_type=='0':
                    content='烟雾传感器'+sensoralarm.sensor_id+'异常'
                elif sensoralarm.sensor_type == '0':
                    content = '温度传感器' + sensoralarm.sensor_id + '异常'
                elif sensoralarm.sensor_type == '0':
                     content = '燃气阀' + sensoralarm.sensor_id + '异常'
                elif sensoralarm.sensor_type == '0':
                    content = '智能插座' + sensoralarm.sensor_id + '异常'
                else: content='电磁阀'+sensoralarm.sensor_id+'异常'
                print('first step')
                list=[]
                for i in sendmessage:
                    list.append(i.user_id)
                    # j=i
                    # if j<len(sendmessage):
                    #     for j in sendmessage :
                    #       if j.message_id==i.message_id:
                    #           list.append(j.user_id)
                    #       else:pass
                    #     else:pass
                    i.if_send = True
                    db.session.commit()
                    taskid=getui.getTaskId(sendmessage.message_id,content)
                    rs=getui.sendList(list, taskid)

def OpenSensor(app):
    with app.app_context():
        sensortimes=SensorTime.query.all()
        for sensortime in sensortimes:
            sensor=Sensor.query.get_or_404(sensortime.sensor_id)
            if sensortime.start_time == datetime.datetime.strftime(datetime.datetime.now(), '%H:%M') and sensortime.\
                    switch_on == True:

                data = {'data': {
                    sensortime.sensor_id: '1'
                },
                    'time': datetime.datetime.now()
                }
                theme = str(sensor.gateway_id) + '/cmd'
                mqtt.publish(theme, json.dumps(data))
            else:
                pass
            if sensortime.end_time == datetime.datetime.strftime(datetime.datetime.now(), '%H:%M') and sensortime.\
                    switch_on == True:
                data = {'data': {
                    sensortime.sensor_id: '0'
                },
                    'time': datetime.datetime.now()
                }
                theme = str(sensor.gateway_id) + '/cmd'
                mqtt.publish(theme, json.dumps(data))
            else:
                pass













