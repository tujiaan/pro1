import datetime

from flask import request, g
from flask_restplus import Namespace, Resource
from sqlalchemy import and_

from app.ext import db
from app.models import Home, Ins, User, HomeUser, Sensor, SensorHistory, UserRole, Role
from app.utils.auth import decode_jwt, user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1 import homeuser
from app.views.api_v1.gateways import gateway_model
from app.views.api_v1.homes.parser import home_parser, home_parser1
from app.views.api_v1.homeuser import HomeUserView1
from app.views.api_v1.institutes import institute_model
from app.views.api_v1.sensors import sensor_model
from app.views.api_v1.tools.database import Utills
from app.views.api_v1.users import user_model
import math

api = Namespace('Home', description='家庭相关接口')
from.model import *



@api.route('/')
class HomesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','homeuser', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询家庭列表')
    @api.marshal_with(home_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list=Home.query
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        homeuser=HomeUser.query.filter(HomeUser.user_id==g.user.id)
        if 'homeuser'in [i.name for i in  roles] and len(roles)<2:
            return list.filter(g.user.id.in_(homeuser.user_id))

        else: return list,200


    @api.doc('新增家庭')
    @api.expect(home_parser)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    def post(self):
        args = home_parser.parse_args()
        home = Home(**args)
        if g.user.contract_tel != args.get('telephone'):
            return '号码不一致', 200
        elif home.gateway_id in [i.gateway_id for i in Home.query.all()]:
            return '网关被占用', 201
        else:
            db.session.add(home)
            db.session.commit()
            homeuser=HomeUser()
            homeuser.if_confirm=True
            homeuser.home_id=home.id
            homeuser.user_id=g.user.id
            homeuser.confirm_time=datetime.datetime.now()
            db.session.add(homeuser)
            db.session.commit()
            return '创建成功', 201

@api.route('/<homeid>')
class HomeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin', 'superadmin'])
    @api.doc('根据家庭id查找家庭')
    @api.marshal_with(home_model)
    @api.response(200,'ok')
    def get(self,homeid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home = Home.query.get_or_404(homeid)
        homeuser=HomeUser.query.filter(HomeUser.home_id==homeid).all()
        if 'homeuser'in [i.name for i in roles] and len(roles)<2:
            if g.user.id in [i.user_id for i in homeuser]:
                return home,200
            else: return '权限不足',201
        else: return home,200

    @api.doc('根据家庭id删除家庭')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin','superadmin'])
    @api.response(200,'ok')
    def delete(self,homeid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home = Home.query.get_or_404(homeid)
        homeuser=HomeUser.query.filter(HomeUser.home_id==homeid).all()
        if  'admin' in [i.name for i in roles]or 'superadmin'in[i.name for i in roles]  :
            for u in homeuser:
                db.session.delete(u)
            db.session.delete(home)
            db.session.commit()
            return None,200
        elif home.admin_user_id==g.user.id:
           for u in homeuser :
               db.session.delete(u )
           db.session.delete(home)
           db.session.commit()
           return None, 200
        else: return '权限不足',200


    @api.doc('根据家庭id更新家庭')
    @api.expect(home_parser1,validate=True)
    @api.marshal_with(home_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.response(200,'ok')
    def put(self,homeid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        args=home_parser1.parse_args()
        home1=Home(**args)
        home = Home.query.get_or_404(homeid)
        if home.admin_user_id == g.user.id or 'admin' in [i.name for i in roles] or 'superadmin' in [i.name for i in roles]:
            if home1.admin_user_id:
                home.admin_user_id=home1.admin_user_id
            else:pass
            if home1.detail_address:
                home.detail_address=home1.detail_address
            if home1.alternate_phone:
                home.alternate_phone=home1.alternate_phone
            else:pass
            if home1.gateway_id:
                home.gateway_id=home1.gateway_id
            else:pass
            if home1.community:
                home.community=home1.community
            else:pass
            if home1.community_id:
             home.community_id=home1.community_id
            else:pass
            if home1.latitude:
             home.latitude=home1.latitude
            else:pass
            if home1.longitude:
             home.longitude=home1.longitude
            else:pass
            if home1.link_name:
             home.link_name=home1.link_name
            else:pass
            if home1.telephone:
                home.telephone=home1.telephone
            else:pass
            if home1.name:
             home.name=home1.name
            else:pass
            if home1.admin_user_id:
                if 'admin' in [i.name for i in  roles] or 'superadmin' in [i.name for i in  roles]:
                 home.admin_user_id=home1.admin_user_id
            db.session.commit()
            return home,200
        else: return '权限不足',200

@api.route('/<homeid>/<gatewayid>')
class HomeGatewayView(Resource):
    @api.doc('更改家庭绑定网关')
    @api.response(200,'ok')
    @api.marshal_with(gateway_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin','superadmin'])

    def post(self,homeid,gatewayid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home=Home.query.get_or_404(homeid)
        if 'homeuser'in [i.name for i in roles] and g.user.id!=home.admin_user_id:
            return '权限不足',301
        else:
            home.gateway_id = gatewayid
            db.session.commit()
            return home,200

    @api.doc('删除家庭的网关')
    @api.response(200, 'ok')
    @role_require(['homeuser','admin', 'superadmin'])
    @api.header('jwt', 'JSON Web Token')
    def delete(self,homeid,gatewayid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home = Home.query.get_or_404(homeid)
        if 'homeuser'in [i.name for i in roles] and g.user.id!=home.admin_user_id:
            return '权限不足',301
        else:
            db.session.delete(home)
            db.session.commit()
            return None,200


@api.route('/<homeid>/users')
class HomeUsersView(Resource):

    @role_require(['homeuser', 'admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查找家庭下的所有用户')
    @api.header('jwt', 'JSON Web Token')
    @api.response(401, '权限不足')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(user_model, as_list=True)
    @page_range()
    def get(self, homeid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home = Home.query.get_or_404(homeid)
        homeuser=HomeUser.query.filter(HomeUser.home_id==homeid).all()
        if g.user.id in [i.user_id for i in homeuser ] or 'admin' in [i.name for i in roles] or 'superadmin' in [
            i.name for i in roles]:
            return User.query.filter(User.id.in_(i.user_id for i in homeuser)), 200
        else:
            return User.query.filter(User.id==g.user.id), 401



    @api.doc('用户退出家庭')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')

    @role_require(['homeuser' ])
    def delete(self, homeid):
        home = Home.query.get_or_404(homeid)
        user=g.user
        homeuser=HomeUser.query.filter(and_(HomeUser.home_id==home.id,HomeUser.user_id==user.id)).first()
        if homeuser:
            db.session.delete(homeuser)
            db.session.commit()
            return '退出家庭成功', 200

        else:return '不是该家庭成员',301

@api.route('/<homeid>/<distance>/ins')
class HomeInsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.doc('查询家庭附近的机构')
    @api.response(200, 'ok')
    def get(self,homeid,distance):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        home=Home.query.get_or_404(homeid)
        homeuser=HomeUser.query.filter(HomeUser.user_id==g.user.id).all()
        def getDistance(lat0, lng0, lat1, lng1):
            lat0 = math.radians(lat0)
            lat1 = math.radians(lat1)
            lng0 = math.radians(lng0)
            lng1 = math.radians(lng1)
            dlng = math.fabs(lng0 - lng1)
            dlat = math.fabs(lat0 - lat1)
            miles = ((69.1 * dlat) ** 2 + (53.0 * dlng) ** 2) ** .5
            return miles * 1.6092953
        query=Ins.query
        query=query.offset((int(page) - 1) * limit).limit(limit)
        _ = []
        for i in tuple(query.all()):
            __ = {}
            __['ins_id'] = i.id
            __['ins_type'] = i.type
            __['ins_place'] = i.name
            __['distance'] = getDistance(i.latitude,i.longitude,home.latitude,home.longitude)
            if  getDistance(i.latitude,i.longitude,home.latitude,home.longitude)<float(distance):
              _.append(__)
        total=len(_)
        result = {
            'code': 0,
            'msg': '200',
            'count': total,
            'data': _
        }
        if homeid in [i.home_id for i in homeuser] or 'admin' in [i.name for i in roles] or 'superadmin' in [i.name for i in roles] :
                return result,200
        else:return '权限不足',201


@api.route('/<homeid>/sensors')
class HomeSensorView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', '119user', 'insuser' 'admin', 'superadmin'])
    @api.doc('查询家中的传感器')
    def get(self, homeid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        home=Home.query.get_or_404(homeid)
        homeuser=HomeUser.query.filter(HomeUser.home_id==homeid).all()
        if  'homeuser' in [i.name for i in roles] and len(roles)<2:
            if g.user.id in [i.user_id for i in homeuser]:
                query=Sensor.query.filter(Sensor.home_id==home.id).all()
            else:pass
        else:query=Sensor.query.all()
        _=[]
        for i in query:
            __={}
            __['sensor_id']=i.id
            __['sensor_place']=i.sensor_place
            __['sensor_type']=i.sensor_type
            sensorhistory=SensorHistory.query.filter(SensorHistory.sensor_id==i.id).order_by(SensorHistory.time.desc()).first()
            if sensorhistory:
             __['state']=sensorhistory.sensor_state
            _.append(__)
        result={
            'data':_
         }
        return result,200

@api.route('/applies/')
class HomeApplyView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @api.doc('显示自己家庭申请')
    @api.response(200,'ok')
    @user_require
    def get(self):
        page = request.args.get('page', 1)
        limit = request.args.get('limit', 10)
        query = db.session.query(User,Home).join(HomeUser,User.id==HomeUser.user_id).filter(HomeUser.if_confirm == False).join(Home,HomeUser.home_id==Home.id ).order_by(Home.id)
        total = query.count()
        query = query.offset((int(page) - 1) * limit).limit(limit)
        _ = []
        for i in query.all():
            __ = {}
            __['user_id'] = i[0].id
            __['contract_tel'] = i[0].contract_tel
            __['user_name'] = i[0].username
            __['home_id'] = i[1].id
            __['home_name'] = i[1].name

            _.append(__)
        result = {
            'code': 200,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        return result

