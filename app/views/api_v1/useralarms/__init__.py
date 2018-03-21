from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import UserAlarmRecord
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.useralarms.parser import useralarmrecord_parser, useralarmrecord1_parser

api=Namespace('UserAlarmsRecords',description='用户报警记录相关操作')
from .models import *
@api.route('/')
class UserAlarmRecordsView(Resource):

    @api.header('jwt', 'JSON Web Token')
    #@role_require(['admin', 'superadmin', 'insuser'])
    @page_format(code=0,msg='ok')
    @api.doc('查询用户报警记录列表')
    @api.marshal_with(useralarmrecord_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list=UserAlarmRecord.query
        if'admin' in [i.name for i in g. user. role] or'superadmin'in [i.name for i in g. user. role]:
            return list,200
        elif'homeuser'in [i.name for i in g. user. role] and len(g.user.roles.all())<2:
            return list.filter(UserAlarmRecord.user in [i.user for i in g.user.home])


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


