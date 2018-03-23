import datetime

from flask import g, request
from flask_restplus import Namespace, Resource
from sqlalchemy import and_

from app.ext import db
from app.models import UserAlarmRecord, Community, Home, User
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.useralarms.parser import useralarmrecord_parser, useralarmrecord1_parser

api=Namespace('UserAlarmsRecords',description='用户报警记录相关操作')
from .models import *
@api.route('/')
class UserAlarmRecordsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'insuser'])
    @api.doc('查询用户报警记录列表')
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量','start':'开始时间','end':'结束时间','type':'类型'})
    def get(self):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        start = request.args.get('start', 2018-1-1 )
        end = request.args.get('end', datetime.datetime.now().isoformat())
        type = request.args.get('type', 0)
        query = db.session.query(UserAlarmRecord,Home,User).join(Home, UserAlarmRecord.home_id==Home.id)\
            .join(User,UserAlarmRecord.user_id==User.id).filter( UserAlarmRecord.time.between(start,end)).\
            filter(UserAlarmRecord.type==type).order_by(UserAlarmRecord.id)
        total = query.count()

        query = query.offset((int(page) - 1) * limit).limit(limit)
        # [{''} for i in query.all()]
        _ = []
        for i in query.all():
            __ = {}
            __['useralarmrecord_id']=i[0].id
            __['useralarmrecord_type']=i[0].type
            __['useralarmrecord_content'] = i[0].content
            __['useralarmrecord_time'] = str(i[0].time)
            __['useralarmrecord_note'] = i[0].note
            __['home_id']=i[1].id
            __['home_name']=i[1].name
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
        return result


    @api.doc('新增用户报警记录(用户提交传感器报警信息)')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
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

    @api.doc('更新用户报警信息（报警确认如果是的要加if_confirm字段）')

    @api.expect(useralarmrecord1_parser)
    @api.response(200,'ok')
    def put(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        args=useralarmrecord1_parser.parse_args()
        if args['type']:
            useralarmrecord.type=args['type']
        else:pass
        if args['content']:
            useralarmrecord.content=args['content']
        else:pass
        if args['community_id']:
            useralarmrecord.community_id=args['community_id']
        else:pass
        if args['user_id']:
            useralarmrecord.user_id=args['user_id']
        else:pass
        db.session.commit()
        return None,200

    @api.doc('删除用户报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([ ])
    @api.response(200, 'ok')
    def delete(self,useralarmrecordid):
        useralarmrecord=UserAlarmRecord.query.get_or_404(useralarmrecordid)
        db.session.delete(useralarmrecord)
        db.session.commit()
        return None,200


