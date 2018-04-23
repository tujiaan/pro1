import datetime
from operator import or_, and_
from flask import app, json
from flask_restplus import abort

from app.ext import db, getui, mqtt
from app.models import Sensor, SensorAlarm, MessageSend, Home, HomeUser, User, Ins, UserAlarmRecord, Role, UserRole, \
    SensorTime


def BuiltSensorSendMessage(app):
    with app.app_context():
        sensoralarm = SensorAlarm.query.all()
        for i in sensoralarm:
            messagesend = MessageSend.query.filter(MessageSend.message_id == i.id).all()
            if len(messagesend) < 1:
                if i.is_confirm==False:
                    home = Home.query.filter(Home.gateway_id == i.gateway_id).filter(Home.disabled == False).first()
                    if home:
                        homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user = User.query.filter(User.id.in_(i.user_id for i in homeuser)).filter(User.disabled == False).all()
                        for j in user:
                            messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=j.id, role_id='1')
                            ms = MessageSend.query.filter(and_(MessageSend.message_id == i.id, MessageSend.user_id == j.id)).first()
                            if ms is None:
                                db.session.add(messagesend)
                                db.session.commit()
                            else:pass
                        if i.is_timeout==True:
                            community = home.community
                            ins = community.ins.all()
                            if len(ins) > 0:
                                for j in ins:
                                    for k in j.user:
                                        if j.type=='物业':
                                            messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=k.id, role_id='2')
                                        else: messagesend = MessageSend(message_id=i.id, message_type='传感器报警', user_id=k.id, role_id='3')
                                        ms = MessageSend.query.filter(
                                            and_(MessageSend.message_id == i.id, MessageSend.user_id == j.id)).first()
                                        if ms is None:
                                            db.session.add(messagesend)
                                            db.session.commit()
                                        else:
                                            pass
                            else:abort(404, message='机构不存在')
                    else: abort(404, message='家庭不存在')
                else:pass
            else: pass
    return None, 200


def BuiltUserSendMessage(app):
    with app.app_context():
        useralarmrecord = UserAlarmRecord.query.all()
        for i in useralarmrecord:
            sendmessage = MessageSend.query.filter(MessageSend.message_id == i.id).all()
            if len(sendmessage) < 1:
                if i.home_id:
                    home = Home.query.filter(Home.id == i.home_id).filter(Home.disabled==False).first()
                    if home:
                        homeuser = HomeUser.query.filter(HomeUser.home_id == i.home_id).all()
                        user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
                        ins = home.community.ins.all()
                    else:abort(404)
                else:
                    ins = Ins.query.filter(Ins.id == i.ins_id).filter(Ins.disabled == False).all()
                list1 = []
                for _ in ins:
                    list1.append(_.user.all())
                    if _.type =='物业':
                        if i.type == 0 or i.type == 1:
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4', UserRole.role_id == '5')).union(
                                UserRole.query.filter((UserRole.role_id == '6'))).all()
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled == False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled == False)
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled == False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        elif i.type == 2:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled == False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled == False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled == False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                          role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        else:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4',UserRole.role_id == '5')).union(UserRole.query.filter((UserRole.role_id=='6'))).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='2')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                    else:
                        if i.type == 0 or i.type == 1:
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '4', UserRole.role_id == '5')).union(
                                UserRole.query.filter((UserRole.role_id == '6'))).all()
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '4'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='4')
                                    elif '5'in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='5')
                                    else:messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        elif i.type == 2:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id == '5', UserRole.role_id == '6')).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                            list2 = query1.union(query2).union(query3).all()
                            for j in list2:
                                if j in query1.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                                elif j in query2.all():
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                                else:
                                    user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                    roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                    if '5' in [i.id for i in roles]:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                          role_id='5')
                                    else:
                                        messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                                  role_id='6')
                                db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                                db.session.commit()
                        else:
                            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1)).filter(User.disabled==False)
                            query2 = User.query.with_entities(User.id).filter(User.id.in_(i[0].id for i in list1)).filter(User.disabled==False)
                            userrole = UserRole.query.filter(or_(UserRole.role_id=='4',UserRole.role_id=='5')).union(UserRole.query.filter((UserRole.role_id=='6'))).all()
                            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole)).filter(User.disabled==False)
                        list2 = query1.union(query2).union(query3).all()
                        for j in list2:
                            if j in query1.all():
                                messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='1')
                            elif j in query2.all():
                                messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id, role_id='3')
                            else:
                                user_role = UserRole.query.filter(UserRole.user_id == j.id).all()
                                roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
                                if '4' in [i.id for i in roles]:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='4')
                                elif '5' in [i.id for i in roles]:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='5')
                                else:
                                    messagesend = MessageSend(message_id=i.id, message_type='用户报警', user_id=j.id,
                                                              role_id='6')
                            db.session.add(messagesend)  ###119 admin superadmin 不会出现在同一人
                            db.session.commit()
            else: pass
        return None, 200


def SendMessage(app):
    with app.app_context():
        sendmessage = MessageSend.query.filter(MessageSend.if_send == False).order_by(MessageSend.message_id).all()
        for i in sendmessage:
            if i.message_type == '传感器报警':
                sensoralarm = SensorAlarm.query.get_or_404(i.message_id)
                if sensoralarm.sensor_type == '0':
                    content = '烟雾传感器'+sensoralarm.sensor_id+'异常'
                elif sensoralarm.sensor_type == '0':
                    content = '温度传感器' + sensoralarm.sensor_id + '异常'
                elif sensoralarm.sensor_type == '0':
                     content = '燃气阀' + sensoralarm.sensor_id + '异常'
                elif sensoralarm.sensor_type == '0':
                    content = '智能插座' + sensoralarm.sensor_id + '异常'
                else: content = '电磁阀'+sensoralarm.sensor_id+'异常'
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
                    taskid = getui.getTaskId(i.message_id, content)
                    rs = getui.sendList(list, taskid)
                    i.if_send = True
                    db.session.commit()


def OpenSensor(app):
    with app.app_context():
        sensortimes = SensorTime.query.all()
        for sensortime in sensortimes:
            sensor = Sensor.query.get_or_404(sensortime.sensor_id)
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


def builtusersendmessage(app):
    with app.app_context:
        useralarmrecords = UserAlarmRecord.query.all()
        messsgesends = MessageSend.query.all()
        for useralarmrecord in useralarmrecords:
            if useralarmrecord.type == '0':
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled == False).filter(Home.id == useralarmrecord.home_id).first()
                    if home:
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in homeusers1)).all()#####报警家庭成员
                        user2 = []###报警家庭上级机构
                        community = home.community.first()
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in userroles4).all())###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5).all())##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6).all())###超级管理员
                        list = []
                        list.extend(user1).expend(user2).extend(user3).expend(user4).extend(user5)
                        for i in list:
                            if i in user1:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if messsgesend not in messsgesends:
                                db.session.commit()
                            else: continue
                    else:abort(404, message='家庭不存在')
                else:
                    ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == useralarmrecord.ins_id).first()
                    if ins:
                        user1 = ins.user.all()##报警机构的用户
                        communitys = ins.community.all()
                        homes = []
                        for community in communitys:
                            homes.extend(community.homes.first())
                        homeuser = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in homes)).all()
                        user2 = User.query.filter(User.disabled==False).filter(User.id.in_(i.user_id for i in homeuser)).all()#####报警机构管辖下的家庭用户
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles4).all())  ###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5).all())  ##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6).all())  ###超级管理员
                        list=[]
                        list.extend(user1).extend(user2).extend(user3).extend(user4).extend(user5)
                        for i in list:
                            if i in user1:
                                if ins.type=='物业':
                                    messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                     message_type='119报警', if_read=False, if_send=False)
                                else:  messsgesend = MessageSend(user_id=i.id, role_id='3', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            else:  messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='119报警', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if messsgesend not in messsgesends:
                                db.session.commit()
                            else:
                                continue
                    else: abort(401, message='机构不存在')
            elif useralarmrecord.type == '1':
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled==False).filter(Home.id==useralarmrecord.home_id).first()
                    if home:
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in homeusers1)).all()  #####发送疏散家庭成员
                        user2 = []  ###发送疏散家庭上级机构
                        community = home.community.first()
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles4).all())  ###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5).all())  ##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6).all())  ###超级管理员
                        list = []
                        list.extend(user1).expend(user2).extend(user3).expend(user4).extend(user5)
                        for i in list:
                            if i in user1:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if messsgesend not in messsgesends:
                                db.session.commit()
                            else:
                                continue
                    else:
                        abort(404, message='家庭不存在')
                else:
                    ins = Ins.query.filter(Ins.disabled == False).filter(Ins.id == useralarmrecord.ins_id).first()
                    if ins:
                        user1 = ins.user.all()  ##报警机构的用户
                        communitys = ins.community.all()
                        homes = []
                        for community in communitys:
                            homes.extend(community.homes.first())
                        homeuser = HomeUser.query.filter(HomeUser.home_id.in_(i.id for i in homes)).all()
                        user2 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in homeuser)).all()  #####报警机构管辖下的家庭用户
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles4).all())  ###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5).all())  ##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6).all())  ###超级管理员
                        list = []
                        list.extend(user1).extend(user2).extend(user3).extend(user4).extend(user5)
                        for i in list:
                            if i in user1:
                                if ins.type == '物业':
                                    messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                              message_type='疏散消息', if_read=False, if_send=False)
                                else:
                                    messsgesend = MessageSend(user_id=i.id, role_id='3', message_id=useralarmrecord.id,
                                                              message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='疏散消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if messsgesend not in messsgesends:
                                db.session.commit()
                            else:
                                continue
                    else:
                        abort(401, message='机构不存在')
            elif useralarmrecord.type == '3':
                if useralarmrecord.home_id:
                    home = Home.query.filter(Home.disabled == False).filter(Home.id == useralarmrecord.home_id).first()
                    if home:
                        homeusers1 = HomeUser.query.filter(HomeUser.home_id == home.id).all()
                        user1 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in homeusers1)).all()#####报警家庭成员
                        user2 = []###求救家庭上级机构
                        community = home.community.first()
                        inses = community.ins.all()
                        for ins in inses:
                            user2.extend(ins.user.all())
                        userroles4 = UserRole.query.filter(UserRole.role_id == '4').all()
                        user3 = User.query.filter(User.disabled == False).filter(User.id.in_(i.user_id for i in userroles4).all())###119用户
                        userroles5 = UserRole.query.filter(UserRole.role_id == '5').all()
                        user4 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles5).all())##平台管理员
                        userroles6 = UserRole.query.filter(UserRole.role_id == '6').all()
                        user5 = User.query.filter(User.disabled == False).filter(
                            User.id.in_(i.user_id for i in userroles6).all())###超级管理员
                        list = []
                        list.extend(user1).expend(user2).extend(user3).expend(user4).extend(user5)
                        for i in list:
                            if i in user1:
                                messsgesend = MessageSend(user_id=i.id, role_id='1', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user2:
                                messsgesend = MessageSend(user_id=i.id, role_id='2', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user3:
                                messsgesend = MessageSend(user_id=i.id, role_id='4', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            elif i in user4:
                                messsgesend = MessageSend(user_id=i.id, role_id='5', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            else:
                                messsgesend = MessageSend(user_id=i.id, role_id='6', message_id=useralarmrecord.id,
                                                          message_type='求救消息', if_read=False, if_send=False)
                            db.session.add(messsgesend)
                            if messsgesend not in messsgesends:
                                db.session.commit()
                            else: continue
                    else:abort(404, message='家庭不存在')
                else:pass