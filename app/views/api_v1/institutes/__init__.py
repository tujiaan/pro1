from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Ins, User, Facility, Community, FacilityIns
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.communities import community_model
from app.views.api_v1.institutes.parser import institutes_parser, institutes_parser1


api = Namespace('Institutes', description='组织相关接口')

from .model import *


@api.route('/')
class InstitutesViews(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', '119user'])
    @page_format(code=0, msg='ok')
    @api.doc('查询所有机构列表')

    @api.marshal_with(institute_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list = Ins.query
        if 'admin'  in [i.name for i in g.user.roles] or 'superadmin'in [i.name for i in g.user.roles]  :

            return list, 200
        else:
            return list.filter(Ins.admin_user_id == g.user.id)

    @api.doc('新增机构')  #
    @api.expect(institutes_parser, validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200, 'ok')
    @user_require
    def post(self):
        args = institutes_parser.parse_args()
        institute = Ins()
        user = User.query.get_or_404(args['admin_user_id'])
        if Ins.query.filter(Ins.latitude!=args['latitude']or Ins.longitude!=args['longitude']):
            institute.name = args['name']
            if 'insuser' in [i.name for i in user.roles]:

                institute.admin_user_id = args['admin_user_id']
            else:

                institute.admin_user_id = g.user.id

            institute.type = args['type']
            institute.ins_address = args['ins_address']
            institute.note = args['note']
            institute.latitude = args['latitude']
            institute.longitude = args['longitude']
            institute.ins_address = args['ins_address']
            institute.location_id = args['location_id']
            if args['ins_picture']:
                institute.ins_picture = args['ins_picture'].read()
            else:
                pass

            institute.location_id = args['location_id']
            db.session.add(institute)
            institute.user.append(user)

            db.session.commit()
            return 'success', 200
        else:return '机构位置已被占用',201

@api.route('/<insid>')#####???????
class InstituteView(Resource):
   # @api.header('jwt', 'JSON Web Token')
    #@role_require(['insuser', 'admin', 'superadmin'])
    @api.doc('根据机构id查询机构')
    @api.marshal_with(institute_model)
    @api.response(200,'ok')
    def get(self,insid):
        institute=Ins.query.get_or_404(insid)
        return institute,200


    @api.doc('根据id更新机构信息')#
    @api.expect(institutes_parser1)
    @api.response(200,'ok')
    @api.marshal_with(institute_model,as_list=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['insuser', 'admin', 'superadmin'])
    def put(self,insid):
        institute = Ins.query.get_or_404(insid)
        args = institutes_parser1.parse_args()
        if 'insuser'in [i.name for i in g .user.roles]and institute.admin_user_id==g.user.id or'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
            if 'name'in args and args['name'] :
                institute.name=args['name']
            else:pass

            if 'admin_user_id'in args and args['admin_user_id']:
                if 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
                    institute.admin_user_id=args['admin_user_id']
                else: pass
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
            if args['location_id']:
                institute.location_id=args['location_id']
            else:pass
            if 'latitude'in args and args['latitude']:
                institute.latitude=args['latitude']
            else:pass
            try:
                institute.ins_picture = args['ins_picture'].read()
            except:
                pass
            db.session.commit()
            return institute,200
        else:return'权限不足',301

    @api.doc('根据id删除机构')##########待测试
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200,'ok')
    def delete(self,insid):
        institute = Ins.query.get_or_404(insid)
        facilityins=FacilityIns.query.filter(FacilityIns.ins_id==insid).all()
        community=Community.query.filter(Community.ins_id==insid).first()
        for i in facilityins:
         db.session.delete(i)
        user=institute.user
        for i in user:
            InsUserView.delete(self,insid,i.id)
        db.session.delete(community)
        db.session.delete(institute)
        db.session.commit()
        return '删除成功',200

@api.route('/<insid>/users')
class InsUsesrView(Resource):
    #@api.header('jwt', 'JSON Web Token')
    #@role_require(['insuser', 'admin', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询机构下面的用户列表')
    @api.marshal_with(user_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        #if g.user.id==ins.admin_user_id or 'admin'ior 'superadmin'in [i.name for i in g.user.roles] :
        return ins.user,200
        #else:return '权限不足，200'

@api.route('/<insid>/users/<userid>')
class InsUserView(Resource):
    @api.doc('增加机构成员/用户绑定机构')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['insuser', 'admin', 'superadmin'])
    @api.response(200,'ok')
    def post(self,insid,userid):

     ins=Ins.query.get_or_404(insid)
     user=User.query.get_or_404(userid)
     if user not in ins.user:
         if g.user.id == ins.admin_user_id or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles] :
                ins.user.append(user)
                db.session.commit()
                return '添加成功',200
         else: return '权限不足',200
     else:return '用户已存在',301


    @api.doc('删除机构成员/解除用户绑定机构')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['insuser', 'admin', 'superadmin'])
    def delete(self, insid, userid):
      ins = Ins.query.get_or_404(insid)
      user = User.query.get_or_404(userid)
      if   user in ins.user:
          if g.user.id == ins.admin_user_id or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
                ins.user.remove(user)
                db.session.commit()
                return '删除成功', 200
          else:return '权限不足',200

      else:return '成员不存在', 301

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











