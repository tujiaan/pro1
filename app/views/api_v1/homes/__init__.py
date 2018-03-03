from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Home, Ins, User
from app.utils.tools.page_range import page_range
from app.views.api_v1.homes.parser import home_parser, home_parser1
from app.views.api_v1.institutes import institute_model
from app.views.api_v1.sensors import sensor_model
from app.views.api_v1.users import user_model
import math

api = Namespace('Home', description='家庭相关接口')
from.model import *



@api.route('/')
class HomesView(Resource):
    @api.doc('查询家庭列表')
    @api.marshal_with(home_model)
    @api.marshal_with(home_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'from':'开始','count':'数量'})
    @page_range()
    def get(self):
        list=Home.query
        return list,200

    @api.doc('新增家庭')
    @api.expect(home_parser)
    @api.response(200,'ok')
    def post(self):
        args=home_parser.parse_args()
        home=Home(**args)
        db.session.add(home)
        db.session.commit()
        return None,200

@api.route('/<homeid>')
class HomeView(Resource):
    @api.doc('根据家庭id查找家庭')
    @api.marshal_with(home_model)
    @api.response(200,'ok')
    def get(self,homeid):
        home=Home.query.filter_by(id=homeid).first()
        return home,200

    @api.doc('根据家庭id删除家庭')
    @api.response(200,'ok')
    def delete(self,homeid):
        home = Home.query.filter_by(id=homeid).first()
        db.session.delete(home)
        db.session.commit()
        return None,200
    @api.doc('根据家庭id更新家庭')
    @api.expect(home_parser1)
    def put(self,homeid):
        args=home_parser1.parse_args()
        home1=Home(**args)
        home = Home.query.filter_by(id=homeid).first()

        if home1.admin_user_id:
            home.admin_user_id=home1.admin_user_id
        else:pass
        if home1.alternate_phone:
            home.alternate_phone=home1.alternate_phone
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

        db.session.commit()
        return None,200
@api.route('/<homeid>/users')
class HomeUsersView(Resource):
    api.doc('查找家庭下的用户')
    @api.marshal_with(user_model,as_list=True)
    def get(self,homeid):
        home=Home.query.get_or_404(homeid)
        return home.user,200

@api.route('/<homeid>/users/<userid>')
class HomeUserView(Resource):
    @api.doc('增加家庭成员/用户绑定家庭')
    @api.response(200,'ok')
    def post(self,homeid,userid):
        #try:
            home=Home.query.get_or_404(homeid)
            user=User.query.get_or_404(userid)
            home.user.append(user)
            db.session.commit()
            return '添加成员成功',200
       # except:
           # return '成员已经存在',200

    @api.doc('删除家庭成员/解除用户绑定家庭')
    @api.response(200, 'ok')
    def delete(self, homeid, userid):
            try:
                home = Home.query.get_or_404(homeid)
                user = User.query.get_or_404(userid)
                home.user.remove(user)
                db.session.commit()
                return '删除成员成功', 200
            except:
                return '成员不存在存在',200



@api.route('/<homeid>,<distance>/ins')
class HomeInsView(Resource):
    @api.doc('查询家庭附近的机构')
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
        for i in ins:
            if distance>=getDistance(home.latitude,home.longitude,i.latitude,i.latitude):
                list.append((ins,distance))
        return sorted(list,key=lambda l:l[1])
@api.route('/<homeid>/sensors')
class HomeSensorView(Resource):
    @api.doc('查询家中的传感器')
    @api.marshal_with(sensor_model, as_list=True)
    @api.doc(params={'from':'开始','count':'数量'})
    @page_range()

    def get(self,homeid):
        home=Home.query.get_or_404(homeid)
        return home.sensor,200









