import datetime

import math
from flask import g, request
from flask_restplus import Namespace, Resource
from sqlalchemy import and_, or_

from app.ext import db, getui
from app.models import UserAlarmRecord, Community, Home, User, Sensor, UserRole, Role, HomeUser, Ins, MessageSend, \
    SensorAlarm, AlarmHandle
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
#from app.utils.myutil.pushmessage import JPush2
from app.views.api_v1.useralarms.parser import useralarmrecord_parser, useralarmrecord1_parser, useralarmrecord2_parser
api = Namespace('UserAlarmsRecords', description='用户报警记录相关操作')
from .models import *


@api.route('/')
class UserAlarmRecordsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'homeuser', 'superadmin', 'propertyuser', '119user', 'stationuser'])
    @api.doc('查询用户报警记录列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量', 'start': '开始时间', 'end': '结束时间', 'type': '类型'})
    def get(self):
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        start = request.args.get('start', 2018-1-1 )
        end = request.args.get('end', datetime.datetime.now())
        type = request.args.get('type', None)
        homeuser = HomeUser.query.filter(HomeUser.user_id==g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        query = db.session.query(UserAlarmRecord, Home, User).join(Home, UserAlarmRecord.home_id == Home.id) \
            .join(User, UserAlarmRecord.user_id == User.id).filter(UserAlarmRecord.time.between(start, end))
        if type!=None:
            query = query.filter(UserAlarmRecord.type == type)
            if g.role.name == 'homeuser':
                query = query. filter(UserAlarmRecord.home_id.in_(i.id for i in home))
            elif g.role.name == 'propertyuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type == '物业').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name == 'stationuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type == '消防站').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name == '119user':
                query = query.filter(UserAlarmRecord.type!=2)
            else:query = query
        else:
            query = query
            if g.role.name == 'homeuser':
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home)).order_by(UserAlarmRecord.id)
            elif g.role.name == 'propertyuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type == '物业').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name == 'stationuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type == '消防站').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name == '119user':
                query = query.filter(UserAlarmRecord.type != 2)
            else:
                query = query
        query = query.order_by(UserAlarmRecord.id).offset((int(page) - 1) * limit).limit(limit)
        total = UserAlarmRecord.query.count()
        def if_timeout(time):
            if abs((time-datetime.datetime.now()).seconds)<60:
                return '未超时'
            else:return '超时'
        _ = []
        for i in query.all():
            __ = {}
            __['useralarmrecord_id']=i[0].id
            __['useralarmrecord_type']=i[0].type
            __['useralarmrecord_content'] = i[0].content
            __['useralarmrecord_time'] = str(i[0].time)
            __['useralarmrecord_note'] = i[0].note
            __['useralarmrecord_is_timeout']= if_timeout(i[0].time)
            __['reference_alarm_id']=i[0].reference_alarm_id
            __['home_id']=i[1].id
            __['community_id']=Home.query.get_or_404(i[1].id).community.id
            __['community_name'] = Home.query.get_or_404(i[1].id).community.name
            __['ins_id']=i[0].ins_id
            __['if_confirm']=i[0].if_confirm
            __['home_name']=i[1].name
            __['detail_address']=i[1].detail_address
            __['user_id']=i[2].id
            __['user_name']=i[2].username
            __['contract_tel']=i[2].contract_tel
            _.append(__)
        result = {
            'code': 200,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result,200

    @api.doc('新增用户报警记录(用户提交传感器报警信息)')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'homeuser', 'superadmin', 'propertyuser', '119user', 'stationuser'])
    @api.expect(useralarmrecord_parser, validate=True)
    @api.response(200, 'ok')
    def post(self):
        args = useralarmrecord_parser.parse_args()
        useralarmrecord = UserAlarmRecord(**args)
        db.session.add(useralarmrecord)
        db.session.commit()
        if args['reference_alarm_id']:
            alarmhandle = AlarmHandle(reference_message_id=args['reference_alarm_id'], type='1', handle_time=datetime.datetime.now(), handle_type='202', user_id=g.user.id)
        else:alarmhandle = AlarmHandle(type='1', handle_time=datetime.datetime.now(), handle_type='200', user_id=g.user.id, reference_message_id=useralarmrecord.id)
        db.session.add(alarmhandle)
        db.session.commit()
        return {'useralarmrecord_id': useralarmrecord.id}, 200


@api.route('/<useralarmrecordid>')
class UserAlarmRecordView(Resource):
    @api.doc('报警更新')
    @api.expect(useralarmrecord1_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['119user', 'propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def put(self, useralarmrecordid):
        useralarmrecord = UserAlarmRecord.query.get_or_404(useralarmrecordid)
        if useralarmrecord.home_id!=None:
            home = Home.query.get_or_404(useralarmrecord.home_id)
            community = home.community
            ins = community.ins
            insuser = []
            for i in ins:
                insuser.extend(i.user)
        else:ins2 = Ins.query.filter(Ins.id == useralarmrecord.ins_id).first()
        args = useralarmrecord1_parser.parse_args()
        if args['note']:
            useralarmrecord.note = args['note']
        else:pass
        if args['reference_alarm_id']:
            useralarmrecord.reference_alarm_id = args['reference_alarm_id']
        else:pass
        if args['if_confirm']:
            if g.role.name in ['propertyuser', 'stationuser']:
                if g.user.id in[i.id for i in insuser] or g.user.id in [i.id for i in ins2.user]:
                    useralarmrecord.if_confirm = True
                else:pass
            else: useralarmrecord.if_confirm = True
        else:pass
        alarmhandle = AlarmHandle(type='1', handle_time=datetime.datetime.now(), handle_type='203', user_id=g.uer.id, reference_message_id=useralarmrecordid,note = args['note'])
        db.session.add(alarmhandle)
        db.session.commit()

        return '修改成功', 200

    @api.doc('查询单条用户报警记录')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.marshal_with(useralarmrecord_model, as_list=False)
    def get(self, useralarmrecordid):
        def GetNearHome(homeid):
            home = Home.query.get_or_404(homeid)
            community = home.community
            home1 = Home.query.all()

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
            list = []
            for i in home1:
                if getDistance(home.latitude, home.longitude, i.latitude, i.longitude) < community.eva_distance:
                    list.append(i)
            for j in list:
                homeuser2 = HomeUser.query.filter(Home.id == j.id).all()
                user4 = User.query.filter(User.id.in_(i.user_id for i in homeuser2)).all()
                return user4
        useralarmrecord = UserAlarmRecord.query.get_or_404(useralarmrecordid)
        if useralarmrecord.home_id != None:
            home = Home.query.get_or_404(useralarmrecord.home_id)
            homeuser = HomeUser.query.filter(HomeUser.home_id == home.id).all()
            user1 = User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()  # 报警家庭成员
        else:
            ins1 = Ins.query.get_or_404(useralarmrecord.ins_id)
            community1 = ins1.community
            home2 = []
            for i in community1:
                home2.extend(i.homes)
            user2 = ins1.user  ##报警机构成员
        if useralarmrecord.home_id!=None:
            ins2 = Home.query.get_or_404(useralarmrecord.home_id).community.ins
            user3 = []
            for i in ins2:
             user3.extend(i.user)  # 报警家庭上级机构下的成员
        else:pass
        if useralarmrecord.type == '0':
            if g.role.name == 'homeuser':
                if g.user.id in [i.id for i in user1]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name in ['propertyuser', 'stationuser']:
                if g.user.id in [i.id for i in user2] or g.user.id in [i.id for i in user3]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            else:
                return useralarmrecord, 200
        elif useralarmrecord.type == '1':
            if g.role.name == 'homeuser':
                homeuser1 = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
                home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser1)).all()
                if g.user.id in [i.id for i in user1] or set(home).issubset(set(home2)):
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name in ['propertyuser', 'stationuser']:
                if g.user.id in [i.id for i in user3] or g.user.id in [i.id for i in user2]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            else:
                return useralarmrecord, 200
        elif useralarmrecord.type == '2':
            if g.role.name == 'homeuser':
                if g.user.id in [i.id for i in user1]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name in ['propertyuser', 'stationuser']:
                if g.user.id in [i.id for i in user3]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name == '119user':
                return '权限不足', 201
            else:
                return useralarmrecord, 200
        else:
            if g.role.name == 'homeuser':
                if g.user.id in [i.id for i in user1] or g.user.id in [i.id for i in GetNearHome(useralarmrecord.home_id)]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name in ['propertyuser', 'stationuser']:
                if g.user.id in [i.id for i in user3]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            else:
                return useralarmrecord, 200

    @api.doc('删除用户报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([ ])
    @api.response(200, 'ok')
    def delete(self, useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        db.session.delete(useralarmrecord)
        db.session.commit()
        return None,200


@api.route('/<useralarmrecordid>/users/')
class UseralarmrecordView2(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('推送')
    @api.response(200, 'ok')
    def post(self, useralarmrecordid):
       useralarmrecord = UserAlarmRecord.query.get_or_404(useralarmrecordid)
       messagesend = MessageSend.query.filter(MessageSend.message_id == useralarmrecordid).filter(MessageSend.if_send == False).all()
       list=[]
       for i in messagesend:
           list.append(i.user_id)
           i.if_send = True
           db.session.commit()
       content=useralarmrecord.content
       taskid=getui.getTaskId(useralarmrecordid, content)
       getui.sendList(alias=list, taskid=taskid)


@api.route('/<referencealarmid>/type')
class ReferenceAlarmIdViews(Resource):
    def get(self, referencealarmid):
        sensoralarm = SensorAlarm.query.filter(SensorAlarm.id == referencealarmid).first()
        if sensoralarm!=None:
            return True
        else:return False


@api.route('/<messageid>/type')
class ReferenceAlarmIdViews(Resource):
    def get(self, messageid):
        sensoralarm = SensorAlarm.query.filter(SensorAlarm.id == messageid).first()
        if sensoralarm != None:
            return True
        else:return False


@api.route('/<messageid>/<user_id>/messagesend')
class MessageSend2Views(Resource):
    def get(self, message_id, user_id):
        messagesend = MessageSend.query.filter(MessageSend.message_id == message_id).filter(MessageSend.user_id == user_id)\
            .first()
        if messagesend==None:
            return True, 200
        else: return False, 200
