import datetime

import math
from flask import g, request
from flask_restplus import Namespace, Resource
from sqlalchemy import and_, or_

from app.ext import db
from app.models import UserAlarmRecord, Community, Home, User, Sensor, UserRole, Role, HomeUser, Ins
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
        ins=Ins.query.filter(Ins.admin_user_id==g.user.id).all()
        community=ins.community
        home1=Home.query.filter(community.contains(Home.community)).all()
        homeuser=HomeUser.query.filter(HomeUser.user_id==g.user.id).all()
        home=Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        query = db.session.query(UserAlarmRecord, Home, User).join(Home, UserAlarmRecord.home_id == Home.id) \
            .join(User, UserAlarmRecord.user_id == User.id).filter(UserAlarmRecord.time.between(start, end))
        if type!=None:
            query= query.filter(UserAlarmRecord.type==type)
            if g.role.name=='homeuser':
                query=query. filter(UserAlarmRecord.home_id.in_(i.id for i in home))
            elif g.role.name in ['propertyuser','stationuser']:
                query=query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1))
            elif g.role.name=='119user':
                query=query.filter(UserAlarmRecord.type==0)
            else:query=query
        else:
            query = query
            if g.role.name == 'homeuser':
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home)).order_by(UserAlarmRecord.id)
            elif g.role.name in ['propertyuser', 'stationuser']:
                query = query.filter(UserAlarmRecord.home_id.in_(i.id for i in home1)).order_by(UserAlarmRecord.id)
            elif g.role.name == '119user':
                query = query.filter(UserAlarmRecord.type == 0)
            else:
                query = query
        query = query.order_by(UserAlarmRecord.id).offset((int(page) - 1) * limit).limit(limit)
        total = query.count()
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
            __['home_id']=i[1].id
            __['home_name']=i[1].name
            __['detail_address']=i[1].detail_address
            __['user_id']=i[2].id
            __['user_name']=i[2].username
            __['contract_tel']=i[2].contract_tel
            if g.role.name!='homeuser':
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
    @api.doc('获得报警推送信息的对象')
    #@api.marshal_with(user_id_model,as_list=False)
    @api.response(200, 'ok')
    def get(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        homeuser = HomeUser.query.filter(HomeUser.home_id == useralarmrecord.home_id).all()
        user1=User.query.filter(User.id.in_(i.user_id for i in homeuser)).all()
        home = Home.query.get_or_404(useralarmrecord.home_id)
        ins = home.community.ins
        list1=[]
        for i in ins:
            list1.append(i.user)
        if useralarmrecord.type==0 or useralarmrecord.type==1 :
            userrole = UserRole.query.filter(or_(UserRole.role_id == 4, UserRole.role_id == 5, UserRole.role_id == 6)).all()
            query1=User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
            query2=User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
            query3=User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

        elif useralarmrecord.type==2:
            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
            query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
            userrole = UserRole.query.filter(or_( UserRole.role_id == 5, UserRole.role_id == 6)).all()
            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))

        else:
            query1 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in user1))
            query2 = User.query.with_entities(User.id).filter(User.id.in_(i.id for i in list1))
            userrole = UserRole.query.filter(or_(UserRole.role_id == 5, UserRole.role_id!=4,UserRole.role_id == 6)).all()
            query3 = User.query.with_entities(User.id).filter(User.id.in_(i.user_id for i in userrole))
        list2 = query1.union(query2).union(query3).all()
        _=[]
        for i in list2:
            __={}
            __['user_id']=i.id
            _.append(__)
        result={
            'data':_
        }
        list=[]
        for i in   result.get('data'):
            list.append(i.get('user_id'))

        return list,200