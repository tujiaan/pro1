import datetime

import math
from flask import g, request
from flask_restplus import Namespace, Resource
from sqlalchemy import and_, or_

from app.ext import db, getui
from app.models import UserAlarmRecord, Community, Home, User, Sensor, UserRole, Role, HomeUser, Ins, MessageSend, \
    SensorAlarm
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
#from app.utils.myutil.pushmessage import JPush2
from app.views.api_v1.useralarms.parser import useralarmrecord_parser, useralarmrecord1_parser, useralarmrecord2_parser
api=Namespace('UserAlarmsRecords',description='用户报警记录相关操作')
from .models import *
@api.route('/')
class UserAlarmRecordsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','homeuser', 'superadmin', 'propertyuser','119user', 'stationuser'])
    @api.doc('查询用户报警记录列表')
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量','start':'开始时间','end':'结束时间','type':'类型'})
    def get(self):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        start = request.args.get('start', 2018-1-1 )
        end = request.args.get('end', datetime.datetime.now().isoformat())
        type = request.args.get('type', None)
        homeuser=HomeUser.query.filter(HomeUser.user_id==g.user.id).all()
        home=Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        query = db.session.query(UserAlarmRecord, Home, User).join(Home, UserAlarmRecord.home_id == Home.id) \
            .join(User, UserAlarmRecord.user_id == User.id).filter(UserAlarmRecord.time.between(start, end))
        if type!=None:
            query= query.filter(UserAlarmRecord.type==type)
            if g.role.name=='homeuser':
                query=query. filter(UserAlarmRecord.home_id.in_(i.id for i in home))
            elif g.role.name == 'propertyuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type=='物业').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query=query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name=='stationuser':
                ins = Ins.query.filter(Ins.user.contains(g.user)).filter(Ins.type == '消防站').all()
                community = []
                for i in ins:
                    community.extend(i.community.all())
                home1 = Home.query.filter(Home.community_id.in_(i.id for i in community)).all()
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name=='119user':
                query=query.filter(UserAlarmRecord.type!=2)
            else:query=query
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
            __['rference_alarm_id']=i[0].reference_alarm_id
            __['home_id']=i[1].id
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
    @role_require(['admin','homeuser', 'superadmin', 'propertyuser','119user', 'stationuser'])
    @api.expect(useralarmrecord_parser,validate=True)
    @api.response(200,'ok')
    def post(self):
        args=useralarmrecord_parser.parse_args()
        useralarmrecord=UserAlarmRecord(**args)
        db.session.add(useralarmrecord)
        db.session.commit()
        return None,200
@api.route('/<useralarmrecordid>')
class UserAlarmRecordView(Resource):
    @api.doc('报警更新')
    @api.expect(useralarmrecord1_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','119user','admin','superadmin'])
    @api.response(200,'ok')
    def put(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        home=Home.query.get_or_404(useralarmrecord.home_id)
        args=useralarmrecord1_parser.parse_args()
        if args['note']:
            useralarmrecord.note= args['note']
        else:pass
        if args['reference_alarm_id']:
            useralarmrecord.reference_alarm_id=args['reference_alarm_id']
        else:pass
        if args['if_confirm']:
            useralarmrecord.if_confirm = True
        else:pass
        if g.role.name=='homeuser':
            if g.user.id==home.admin_user_id:
                db.session.commit()
                return None,200
            else:return '权限不足',201
        else:db.session.commit()
        return None,200



    @api.doc('查询单条用户报警记录')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.marshal_with(useralarmrecord_model,as_list=False)
    def get(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        home=Home.query.get_or_404(useralarmrecord.home_id)
        homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
        community=home.community
        ins=community.ins
        if useralarmrecord.type==0:
            if g.role.name=='homeuser':
                if g.user.id==home.admin_user_id:
                    return useralarmrecord,200
                else: return '权限不足',201
            elif g.role.name=='119user':
                return useralarmrecord, 200
            elif g.role.name in['propertyuser','stationuser']:
                if g.user.id in[i.admin_user_id for i in ins]:
                    return useralarmrecord, 200
                else: return '权限不足', 201
            else :return useralarmrecord, 200
        elif useralarmrecord.type==1:
            if g.role.name=='homeuser':
                if g.user.id in[i.user_id for i in homeuser]:
                    return useralarmrecord,200
                else:return'权限不足',201
            elif g.role.name in ['propertyuser','stationuser']:
                if g.user.id in[i.admin_user_id for i in ins]:
                    return useralarmrecord,200
                else:return '权限不足', 201
            else:return useralarmrecord,200
        elif useralarmrecord.type==2:
            if g.role.name=='homeuser':
                if g.user.id in[i.user_id for i in homeuser]:
                    return useralarmrecord,200
                else:return'权限不足',201
            elif g.role.name in ['propertyuser','stationuser','119user']:
                if g.user.id in [i.admin_user_id for i in ins]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            else: return useralarmrecord,200
        elif useralarmrecord.type==3:
            if g.user.id==useralarmrecord.user_id:
                return useralarmrecord,200
            elif g.role.name in['propertyuser','stationuser']:
                if g.user.id in [i.admin_user_id for i in ins]:
                    return useralarmrecord, 200
                else:
                    return '权限不足', 201
            elif g.role.name in['admin','superadmin']:
                return  useralarmrecord, 200
            else:return'权限不足',201


    @api.doc('删除用户报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([ ])
    @api.response(200, 'ok')
    def delete(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        db.session.delete(useralarmrecord)
        db.session.commit()
        return None,200
@api.route('/<useralarmrecordid>/users/')
class UseralarmrecordView2(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser','stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('推送')
    #@api.marshal_with(user_id_model,as_list=False)
    @api.response(200, 'ok')
    def get(self,useralarmrecordid):
       useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
       messagesend=MessageSend.query.filter(MessageSend.message_id==useralarmrecordid).filter(MessageSend.if_send==False).all()
       list=[]
       for i in messagesend:
           list.append(i.user_id)
           i.if_send = True
           db.session.commit()
       content=useralarmrecord.content
       taskid=getui.getTaskId(content)
       getui.sendList(alias=list,taskid=taskid)


       # result={
       #     'content':content,
       #     'list':list
       # }
       # return result,200
@api.route('/<referencealarmid>/type')
class ReferenceAlarmIdViews(Resource):
    def get(self,referencealarmid):
        sensoralarm=SensorAlarm.query.filter(SensorAlarm.id==referencealarmid).first()
        if sensoralarm!=None:
            return True
        else:return False