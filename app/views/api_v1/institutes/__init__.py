from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Ins
from app.utils.tools.page_range import page_range
from app.views.api_v1.institutes.parser import institutes_parser, institutes_parser1

api = Namespace('Institutes', description='组织相关接口')
#from app.views.api_v1.institutes.model import institute_model
from .model import *

@api.route('/')
class InstitutesViews(Resource):
    @api.doc('查询所有机构列表')
    @api.marshal_with(institute_model, as_list=True )
    @api.response(200,'ok')
    @api.doc(params={'from': '开始', 'count': '数量'})
    @page_range()
    def get(self):
        list = Ins .query
        return list, 200
    @api.doc('新增机构')
    @api.expect(institutes_parser)
    @api.response(200,'ok')
    def post(self):
        args=institutes_parser.parse_args()
      #  institute=Ins(**args)
#####################################
        institute=Ins()
        institute.name=args['name']
        institute.admin_user_id=args['admin_user_id']
        institute.type=args['type']
        institute.ins_address=args['ins_address']
        institute.note=args['note']
        institute.latitude=args['latitude']
        institute.longitude=args['longitude']
        institute.ins_address=args['ins_address']
        if args['ins_picture']:
            institute.ins_picture=args['ins_picture'].read()
            db.session.add(institute)
            db.session.commit()
            return None,200

@api.route('/<insid>')
class InstituteView(Resource):
    @api.doc('根据机构id查询机构')
    @api.marshal_with(institute_model)
    @api.response(200,'ok')
    def get(self,insid):
        institute=Ins.query.filter_by(id=insid).first()
        return institute,200


    @api.doc('根据id更新机构信息')
    @api.expect(institutes_parser1)
    @api.response(200,'ok')
    def put(self,insid):
        institute = Ins.query.filter_by(id=insid).first()
        args = institutes_parser1.parse_args()
        if args['name'] :
            institute.name=args['name']
        else:pass
        if args['admin_user_id']:
            institute.admin_user_id=args['admin_user_id']
        else:pass
        if args['type']:
            institute.type=args['type']
        else:pass
        if args['ins_address']:
            institute.ins_address=args['ins_address']
        else:pass
        if args['note']:
            institute.note=args['note']
        else:pass
        if args['longitude']:
            institute.longitude=args['longitude']
        else:pass
        if args['latitude']:
            institute.latitude=args['latitude']
        else:pass
        if args['ins_picture']:
            institute.ins_picture = args['ins_picture'].read()
        else:pass
        db.session.commit(institute)
        return None,200

    @api.doc('根据id删除机构')
    @api.response(200,'ok')
    def delete(self,insid):
        institute = Ins.query.filter_by(id=insid).first()
        db.session.delete(institute)
        db.session.commit()
        return None,200











