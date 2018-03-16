from flask import g
from flask_restplus import Namespace, Resource

from app.models import SensorHistory, Sensor, Home, HomeUser
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_format, page_range

api = Namespace('SensorHistory', description='传感器历史相关接口')
from .models import *
@api.route('/')
class SensorHistoriesView(Resource):
    @api.doc('查询所有传感器的历史')
    @page_format(code=0, msg='ok')

    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','insuser','admin', 'superadmin', '119user'])
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        if 'homeuser'not in [i.name for i in g. user.roles]:
            return SensorHistory.query,200
        else :
            return SensorHistory.query.filter((Sensor.query.get_or_404(SensorHistory.sensor_id)).home.admin_user_id==g.user.id),200
@api.route('/<sensorid>')
class SensorHistoryView(Resource):
    @api.doc('查询特定传感器的历史')
    @page_format(code=0, msg='ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'insuser', 'admin', 'superadmin', '119user'])
    @api.marshal_with(sensorhistory_model, as_list=True)
    @api.response(200, 'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        home=Home.query.get_or_404(sensor.sensorid)
        sensorhistory=SensorHistory.query.filter(SensorHistory.sensor_id==sensorid)
        if 'homeuser'not in [i.name for i in g.user]:
            return sensorhistory,200
        elif g.user.id in [i.user_id for i in (HomeUser.query.filter(HomeUser.home_id==home.id))]:
            return sensorhistory,200
        else:pass
