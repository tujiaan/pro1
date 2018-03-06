from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Ins, User
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.communities import community_model
from app.views.api_v1.institutes.parser import institutes_parser, institutes_parser1


api = Namespace('Institutes', description='组织相关接口')
#from app.views.api_v1.institutes.model import institute_model
from .model import *

@api.route('/')
class InstitutesViews(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询所有机构列表')
    @api.marshal_with(institute_model, as_list=True )
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
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
@api.route('/<insid>/users')
class InsUsesrView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询机构下面的用户列表')
    @api.marshal_with(user_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        return ins.user,200

@api.route('/<insid>/users/<userid>')
class InsUserView(Resource):
    @api.doc('增加机构成员/用户绑定机构')
    @api.response(200,'ok')
    def post(self,insid,userid):
        try:
            ins=Ins.query.get_or_404(insid)
            user=User.query.get_or_404(userid)
            ins.user.append(user)
            db.session.commit()
            return '添加成功',200
        except:
            return '成员已经存在',200

    @api.doc('删除机构成员/解除用户绑定机构')
    @api.response(200, 'ok')
    def delete(self, insid, userid):
        try:
            ins = Ins.query.get_or_404(insid)
            user = User.query.get_or_404(userid)
            ins.user.remove(user)
            db.session.commit()
            return '删除成功', 200
        except:
            return '成员不存在', 200






@api.route('/<insid>/community')
class InsCommunityView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询机构覆盖的社区')
    @api.marshal_with(community_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'from': '开始', 'count': '数量'})
    @page_range()
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        return ins.community,200











