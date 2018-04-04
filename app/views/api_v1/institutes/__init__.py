from flask import g, request
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Ins, User, FacilityIns, UserRole, Role, Location
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.utils.tools.upload_file import upload_file
from app.views.api_v1.institutes.parser import institutes_parser, institutes_parser1
from app.views.api_v1.homes import *

api = Namespace('Institutes', description='组织相关接口')

from .model import *


@api.route('/')
class InstitutesViews(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin', 'superadmin','propertyuser','stationuser', '119user'])
    @api.doc('查询所有机构列表')
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    def get(self):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        list = Ins.query
        if g.role.name in ['propertyuser','stationuser','admin','119user','superadmin']:
           query=list
        else:
            query= list.filter(Ins.admin_user_id == g.user.id)
        query=query.order_by(Ins.id).offset((int(page) - 1) * int(limit)).limit(int(limit))
        total=query.count()
        _=[]
        for i in query.all():
            __={}
            __['ins_id']=i.id
            __['ins_type']=i.type
            __['ins_name']=i.name
            __['ins_picture']=i.ins_picture
            __['location_id']=i.location_id
            __['location_district']=Location.query.get_or_404(i.location_id).district
            __['ins_address']=i.ins_address
            __['ins_note']=i.note
            __['longitude']=str(i.longitude)
            __['latitude']=str(i.latitude)
            __['admin_user_id']=i.admin_user_id
            __['admin_name']=User.query.get_or_404(i.admin_user_id).username
            _.append(__)
        result={
            'code':0,
            'msg':'ok',
            'count':total,
            'data':_
        }
        return result,200



    @api.doc('新增机构')
    @api.expect(institutes_parser, validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200, 'ok')
    @user_require
    def post(self):
        args = institutes_parser.parse_args()
        institute = Ins()
        user = User.query.get_or_404(args['admin_user_id'])
        user_role = UserRole.query.filter(UserRole.user_id == user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        if Ins.query.filter(Ins.latitude!=args['latitude']or Ins.longitude!=args['longitude']):
            institute.name = args['name']
            if 'insuser' in [i.name for i in roles]:
                institute.admin_user_id = args['admin_user_id']
            else:
                institute.admin_user_id = g.user.id
            institute.type = args['type']
            institute.ins_address = args['ins_address']
            institute.note = args['note']
            institute.latitude = args['latitude']
            institute.longitude = args['longitude']
            institute.ins_address = args['ins_address']
            #institute.location_id = args['location_id']
            institute.ins_picture = upload_file(args['ins_picture'])
            # if args['ins_picture']:
            #     institute.ins_picture = args['ins_picture'].read()
            # else:
            #     pass
            institute.location_id = args['location_id']
            db.session.add(institute)
            institute.user.append(user)
            db.session.commit()
            return 'success', 200
        else:return '机构位置已被占用',201

@api.route('/<insid>')
class InstituteView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser', 'stationuser','admin', 'superadmin'])
    @api.doc('根据机构id查询机构')
  #  @api.marshal_with(institute_model)
    @api.response(200,'ok')
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        instute={
            'ins_id':ins.id,
            'ins_admin':ins.admin_user_id,
            'admin_name':User.query.get_or_404(ins.admin_user_id).username,
            'admin_tel':User.query.get_or_404(ins.admin_user_id).contract_tel,
            'type':ins.type,
            'ins_name':ins.name,
            'ins_picture':ins.ins_picture,
            'ins_address':ins.ins_address,
            'location_id':ins.location_id,
            'location_district':Location.query.get_or_404(ins.location_id).district,
            'longitude':str(ins.longitude),
            'latitude':str(ins.latitude),
            'note':ins.note
        }
        # if g.role.name in ['propertyuser','stationuser']:
        #     if ins.admin_user_id!=g.user.id:
        #         return '权限不足',201
        #     else: return instute,200
        # else:
        return instute,200


    @api.doc('根据id更新机构信息')
    @api.expect(institutes_parser1)
    @api.response(200,'ok')
   # @api.marshal_with(institute_model,as_list=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser', 'admin', 'superadmin'])
    def put(self,insid):
        institute = Ins.query.get_or_404(insid)
        args = institutes_parser1.parse_args()
        if 'name'in args and args['name'] :
            institute.name=args['name']
        else:pass
        if 'admin_user_id'in args and args['admin_user_id']:
            if g.role.name in ['admin','superadmin']:
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
            if args['ins_picture']:
                institute.ins_picture =upload_file( args['ins_picture'])
            else:pass
        except:pass
        if g.role.name in ['propertyuser','stationuser']:
            if institute.admin_user_id == g.user.id:
                db.session.commit()
                return institute,200
            else:return '权限不足', 301
        elif g.role.name in ['admin','superadmin']:
            db.session.commit()
            return '修改成功', 200
        else:return'权限不足',301

    @api.doc('根据id删除机构')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.response(200,'ok')
    def delete(self,insid):
        institute = Ins.query.get_or_404(insid)
        facilityins=FacilityIns.query.filter(FacilityIns.ins_id==insid).all()
        for i in facilityins:
         db.session.delete(i)
        list=institute.user
        for i in list:
            institute.user.remove(i)
        for i in  institute.community:
            institute.community.remove(i)
        db.session.delete(institute)
        db.session.commit()
        return '删除成功',200
@api.route('/<insid>/<distance>/ins')
class InsIns(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser','admin', 'superadmin'])
    @api.doc('查询机构附近的机构')
    @api.doc(params={'page':'页数','limit':'数量'})
    @api.response(200,'ok')
    def get(self,insid,distance):
        distance=request.args.get('distance',200)
        page=request.args.get('page',1)
        limit=request.args.get('limit',10)
        ins=Ins.query.get_or_404(insid)
        query=Ins.query.offset((int(page) - 1) * limit).limit(limit)
        _=[]
        for i in query.all():
            __={}
            __['ins_id']=i.id
            __['ins_type']=i.type
            __['ins_name']=i.name
            __['longitude']=str(i.longitude)
            __['latitude']=str(i.latitude)
            __['ins_picture']=i.ins_picture
            __['distance'] = round(HomeInsView.getDistance(i.latitude,i.longitude,ins.latitude,ins.longitude))
            if HomeInsView.getDistance(i.latitude,i.longitude,ins.latitude,ins.longitude)<float(distance):
              _.append(__)
        total=len(_)
        result={
            'code':0,
            'msg':'ok',
            'count':total,
            'data':_
        }
        return result,200


@api.route('/<insid>/users')
class InsUsesrView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser', 'admin', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询机构下面的用户列表')
    @api.marshal_with(user_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        if g.user.id==ins.admin_user_id or g.role.name in ['admin','superadmin'] :
            return ins.user,200
        else:return g.user,201

@api.route('/<insid>/users/<userid>')
class InsUserView(Resource):
    @api.doc('增加机构成员/用户绑定机构')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser', 'admin', 'superadmin'])
    @api.response(200,'ok')
    def post(self,insid,userid):
     ins=Ins.query.get_or_404(insid)
     user=User.query.get_or_404(userid)
     if user not in ins.user:
         if g.user.id == ins.admin_user_id or g.role.name in ['admin','admin'] :
                ins.user.append(user)
                db.session.commit()
                return '添加成功',200
         else: return '权限不足',200
     else:return '用户已存在',301


    @api.doc('删除机构成员/解除用户绑定机构')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser', 'admin', 'superadmin'])
    def delete(self, insid, userid):
      user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
      roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
      ins = Ins.query.get_or_404(insid)
      user = User.query.get_or_404(userid)
      if  user in ins.user:
          if g.user.id == ins.admin_user_id or g.role.name in ['admin', 'admin']:
                ins.user.remove(user)
                db.session.commit()
                return '删除成功', 200
          else:return '权限不足',200

      else:return '成员不存在', 301

@api.route('/<insid>/community')
class InsCommunityView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询机构覆盖的社区')
    @ api.header('jwt', 'JSON Web Token')
    @ role_require(['propertyuser', 'stationuser', 'admin', 'superadmin'])
    @api.marshal_with(community_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,insid):
        ins=Ins.query.get_or_404(insid)
        return ins.community,200














