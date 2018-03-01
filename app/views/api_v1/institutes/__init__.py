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
        else:pass
        db.session.add(institute)
        db.session.commit()
        return None,200

@api.route('/<insid>')
class InstituteView(Resource):
    @api.doc('根据机构id查询机构')
    @api.marshal_with(institute_model)
    @api.response(200,'ok')
    def get(self,insid):
        institute=Ins.query.get_or_404(insid)
        return institute,200


    @api.doc('根据id更新机构信息')
    @api.expect(institutes_parser1)
    @api.response(200,'ok')
    def put(self,insid):
        institute = Ins.query.get_or_404(insid)
        args = institutes_parser1.parse_args()
        if 'name'in args and args['name'] :
            institute.name=args['name']
        else:pass
        if 'admin_user_id'in args and args['admin_user_id']:
            institute.admin_user_id=args['admin_user_id']
        else:pass
        if 'type'in args and args['type']:
            institute.type=args['type']
        else:pass
        if 'ins_address'in args and args['ins_address']:
            institute.ins_address=args['ins_address']
        else:pass
        if 'note'in args and args['note']:
            institute.note=args['note']
        else:pass
        if 'longitude'in args and args['longitude']:
            institute.longitude=args['longitude']
        else:pass
        if 'latitude'in args and args['latitude']:
            institute.latitude=args['latitude']
        else:pass
        try:
            institute.ins_picture = args['ins_picture'].read()
        except:
            pass
        db.session.commit()
        return None,200

    @api.doc('根据id删除机构')
    @api.response(200,'ok')
    def delete(self,insid):
        institute = Ins.query.get_or_404(insid)
        db.session.delete(institute)
        db.session.commit()
        return None,200
@api.route('/<insid>/user')
class InsUserView(Resource):
    @api.doc('查询机构下面的用户列表')
    @api.marshal_with(user_model,as_list=True)
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        return ins.user,200










