from flask import g
from flask_restplus import Namespace, Resource

from app.models import SensorHistory, Sensor, Home, HomeUser, UserRole, Role
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_format, page_range

api = Namespace('SensorHistory', description='传感器历史相关接口')
from .models import *
@api.route('/')
class SensorHistoriesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser', 'stationuser', 'admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询所有传感器的历史')
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        sensor = Sensor.query.filter(Sensor.home_id.in_(i.id for i in home)).all()
        if g.role.name=='homeuser':
            return SensorHistory.query.filter(SensorHistory.sensor_id.in_(i.id for i in sensor)),200
        else: return SensorHistory.query,200

@api.route('/<sensorid>')
class SensorHistoryView(Resource):
    @api.doc('查询特定传感器的历史')
    @page_format(code=0, msg='ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser', 'admin', 'superadmin'])
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,sensorid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        sensor=Sensor.query.get_or_404(sensorid)
        home=Home.query.filter(Home.sensor.contains(sensor)).first()
        sensorhistory=SensorHistory.query.filter(SensorHistory.sensor_id==sensorid)
        homeuser=HomeUser.query.filter(HomeUser.home_id==home.id)
        if g.role.name=='homeuser':
            if g.user.id in [i.user_id for i in homeuser]:
                return sensorhistory, 200
            else: pass
        else:
            return sensorhistory,200

