from flask import request, g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Home, Ins, User, HomeUser, Sensor
from app.utils.auth import decode_jwt
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
        if 'admin'or 'superadmin'in [i.name for i in g.user.roles]:
            return list,200
        else:
            return list.filter(g.user in [Home.user] )

    @api.doc('新增家庭')
    @api.expect(home_parser)
    @api.response(200, 'ok')
    # @api.marshal_with(home_model)
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
            userid=g.user.id
            homeid=home.id
            #homeuser.HomeUserView1.post(homeid )
            Utills.post1(homeid )##########################待测试创建家庭后就是自动在homeuser中添加一行记录
            db.session.commit()
            return '创建成功', 201

@api.route('/<homeid>')
class HomeView(Resource):
    @api.doc('根据家庭id查找家庭')
    @api.marshal_with(home_model)
    @api.response(200,'ok')
    def get(self,homeid):
        home=Home.query.get_or_404(homeid)
        return home,200

    @api.doc('根据家庭id删除家庭')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin','superadmin'])
    @api.response(200,'ok')
    def delete(self,homeid):
        home = Home.query.get_or_404(homeid)

        if home.admin_user_id==g.user.id or 'admin' in [i.name for i in g.user.roles]or 'superadmin'in[i.name for i in g.user.roles]  :
            db.session.delete(home)
            db.session.commit()
            return None,200
        else: return '权限不足',200


    @api.doc('根据家庭id更新家庭')######待测
    @api.expect(home_parser1,validate=True)
    @api.marshal_with(home_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])

    def put(self,homeid):
        args=home_parser1.parse_args()
        home1=Home(**args)
        home = Home.query.get_or_404(homeid)
        if home.admin_user_id == g.user.id or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
            if home1.admin_user_id:
                home.admin_user_id=home1.admin_user_id
            else:pass
            if home1.alternate_phone:
                home.alternate_phone=home1.alternate_phone
            else:pass
            if home1.gateway_id:
               if 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
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
                home.admin_user_id=home1.admin_user_id
            db.session.commit()
            return home,200
        else: return '权限不足',200

@api.route('/<homeid> ,<gatewayid>')######待测
class HomeGatewayView(Resource):
    @api.doc('更改家庭绑定网关')
    @api.response(200,'ok')
    @api.marshal_with(gateway_model)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','admin','superadmin'])

    def post(self,homeid,gatewayid):
        home=Home.query.get_or_404(homeid)

        if 'homeuser'in [i.name for i in g.user.roles] and g.user.id!=home.admin_user_id:
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
        home = Home.query.get_or_404(homeid)
        if 'homeuser'in [i.name for i in g.user.roles] and g.user.id!=home.admin_user_id:
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
        home = Home.query.get_or_404(homeid)
        if g.user.id in [i.id for i in home.user] or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [
            i.name for i in g.user.roles]:
            return home.user, 200
        else:
            return User.query.filter(User.id==g.user.id), 401


@api.route('/<homeid>/users/<userid>')
class HomeUserView(Resource):
    @api.doc('增加家庭成员/用户绑定家庭')
    @api.response(200,'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser' ])
    def post(self,homeid,userid):

            home=Home.query.get_or_404(homeid)
            user=User.query.get_or_404(userid)
            if user not in home.user:
                if home.admin_user_id == g.user.id or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
                    home.user.append(user)
                    db.session.commit()
                    return '添加成员成功',200
                else:
                    return '权限不足',200
            else:return '成员已经存在',301

    @api.doc('删除家庭成员/解除用户绑定家庭')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser' ])
    def delete(self, homeid, userid):
        home = Home.query.get_or_404(homeid)
        user = User.query.get_or_404(userid)
        if user in home.user:
          if home.admin_user_id == g.user.id or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles]:
            home.user.remove(user)
            db.session.commit()
            return '删除成员成功', 200
          else:return '权限不足',200
        else:return '成员不存在',301



@api.route('/<homeid>,<distance>/ins')
class HomeInsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询家庭附近的机构')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    @api.marshal_with(institute_model,as_list=True)
    @api.response(200,'ok')
    def get(self,homeid,distance):
        home=Home.query.get_or_404(homeid)
        ins=Ins.query.all()
        list=[]

        def getDistance(latA, lonA, latB, lonB):
            ra = 6378140  # radius of equator: meter
            rb = 6356755  # radius of polar: meter
            flatten = (ra - rb) / ra  # Partial rate of the earth
            # change angle to radians
            radLatA = math.radians(latA)
            radLonA =math. radians(lonA)
            radLatB = math.radians(latB)
            radLonB = math.radians(lonB)

            pA = math.atan(rb / ra * math.tan(radLatA))
            pB = math.atan(rb / ra * math.tan(radLatB))
            x = math.acos(math.sin(pA) * math.sin(pB) +math. cos(pA) * math.cos(pB) * math.cos(radLonA - radLonB))
            c1 = (math.sin(x) - x) * (math.sin(pA) +math. sin(pB)) ** 2 / math.cos(x / 2) ** 2
            c2 = (math.sin(x) + x) * (math.sin(pA) - math.sin(pB)) ** 2 / math.sin(x / 2) ** 2
            dr = flatten / 8 * (c1 - c2)
            distance = ra * (x + dr)
            return distance

        if home in g.user.home or 'admin' in [i.name for i in g.user.roles] or 'superadmin' in [i.name for i in g.user.roles] :
            for i in ins:
                if distance>=getDistance(home.latitude,home.longitude,i.latitude,i.latitude):
                    list.append((ins,distance))
            return sorted(list,key=lambda l:l[1])
        else:return '权限不足',200


@api.route('/<homeid>/sensors')
class HomeSensorView(Resource):
    @page_format(code=0, msg='ok')
    @api.doc('查询家中的传感器')
    @api.marshal_with(sensor_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})

    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','119user','insuser' 'admin', 'superadmin'])

    @page_range()
    def get(self,homeid):
        homeuser=HomeUser.query.filter(HomeUser.home_id==homeid)
        #print(homeuser)
        home=Home.query.get_or_404(homeid)
       # print(home)
        if 'homeuser' not in[i.name for i in g.user.roles] :

            list = Sensor.query.filter(Sensor.home_id==homeid)
            #print(list.all())
            return list ,200

        else:
            list=Sensor.query.filter(Sensor.home_id in  [i.home_id for i in [HomeUser.query.filter(HomeUser.user_id==g.user.id)]] )
            return list ,200












