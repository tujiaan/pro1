from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Community, Ins, Home, UserRole, Role
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1 import homes

from app.views.api_v1.communities.parser import community_parser, community_parser1


api=Namespace('Community',description='社区相关操作')
from app.views.api_v1.communities.models import community_model, _community_model, home_model
@api.route('/')
class CommunitiesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', '119user','superadmin'])
    @api.doc('查询所有的社区列表')#
    @page_format(code=0,msg='ok')
    @api.marshal_with(community_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        community=Community.query
        print(type(community))
        return community,200

    @api.route('/showlist')
    class CommunitiesView1(Resource):
        @api.header('jwt', 'JSON Web Token')
        @api.doc('查询所有的社区名称')  #
        @page_format(code=0, msg='ok')
        @api.marshal_with(_community_model, as_list=True)
        @api.response(200, 'ok')
        @api.doc(params={'page': '页数', 'limit': '数量'})
        @page_range()
        def get(self):
            community = Community.query
            return community, 200

    @api.doc('新增社区')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.expect(community_parser,validate=True)
    @api.response(200,'ok')
    def post(self):
        args=community_parser.parse_args()
        community=Community()
        if 'name'in args:
            community.name=args.get('name',None)
        else:pass
        if 'ins_id'in args:
            community.ins_id=args.get('ins_id',None)
        else:pass
        if 'longitude'in args:
            community.longitude=args.get('longitude',None)
        else:pass
        if 'latitude'in args:
            community.latitude=args.get('latitude',None)
        else:pass
        if 'save_distance'in args:
            community.save_distance=args.get('save_distance',None)
        else:pass
        if 'eva_distance'in args:
            community.eva_distance=args.get('eva_distance',None)
        else:pass
        if 'detail_address'in args:
            community.detail_address=args.get('detail_address',None)
        else:pass
        if args['community_picture']:
            community.community_picture= args['community_picture'].read()
        else:pass
        if args['location_id']:
            community.location_id=args['location_id']
        else:pass
        db.session.add(community)
        db.session.commit()
        return None,200
@api.route('/<communityid>/')
class CommunityView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','119user','insuser' ,'superadmin'])
    @api.doc('查询特定的小区信息')
    @api.marshal_with(community_model)
    @api.response(200,'ok')
    def get(self,communityid):
        community=Community.query.get_or_404(communityid)
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()

        if 'insuser'not in [i.name for i in roles]:
            return community, 200
        elif g.user.id==community.ins.admin_user_id:
            return community, 200
        else:

            return None, 200


    @api.doc('更新社区的信息')
    @api.expect(community_parser1)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','superadmin' ])
    @api.response(200,'ok')
    def put(self,communityid):
        args=community_parser1.parse_args()
        community = Community.query.get_or_404(communityid)
        if 'name' in args and args['name']:
            community.name = args.get('name')
        else:
            pass
        if 'ins_id' in args and args['ins_id']:
            community.ins_id = args.get('ins_id')
        else:
            pass
        if 'longitude' in args and args['longitude']:
            community.longitude = args.get('longitude')
        else:
            pass
        if 'latitude' in args and args['latitude']:
            community.latitude = args.get('latitude')
        else:
            pass
        if 'save_distance' in args and args['save_distance']:
            community.save_distance = args.get('save_distance')
        else:
            pass
        if 'eva_distance' in args and args['eva_distance']:
            community.eva_distance = args.get('eva_distance')
        else:
            pass
        if 'detail_address' in args and args['detail_address']:
            community.detail_address = args.get('detail_address')
        else:
            pass
        if args['community_picture']:
            community.community_picture = args['community_picture'].read()
        else:
            pass
        if args['location_id']:
            community.location_id=args['location_id']
        else:pass
        db.session.commit()
        return None,200

    @api.doc('删除社区')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin',  'superadmin'])
    @api.response(200,'ok')
    def delete(self,communityid):
        community=Community.query.get_or_404(communityid)
        home=Home.query.filter(Home.id.in_( i.id for i in community.homes))
        for i in home:
          homes.HomeView.delete(self,i.id)
        db.session.delete(community)
        db.session.commit()
        return None,200
@api.route('/<communityid>/homes')
class CommunityHome(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', '119user', 'insuser', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询社区覆盖的家庭')
    @api.marshal_with(home_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    @api.response(200,'ok')
    def get(self,communityid):
        community=Community.query.get_or_404(communityid)
        return community.homes,200





