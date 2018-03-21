from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import SensorAlarm, Home
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms.parser import sensoralarms_parser, sensoralarms_parser1

api=Namespace('Sensoralarms',description='传感器报警相关操作')
from .models import *
@api.route('/')
class SensorAlarmsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询传感器报警记录列表')
    @api.marshal_with(sensoralarms_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list=SensorAlarm.query
        return list,200

    @api.doc('新增传感器报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
    @api.expect(sensoralarms_parser)
    @api.response(200,'ok')
    def post(self):
     args=sensoralarms_parser.parse_args()
     sensoralarm=SensorAlarm(**args)
     db.session.add(sensoralarm)
     db.session.commit()
     return None,200
@api.route('/<sensoralarmid>')
class SensorAlarmView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.doc('根据报id查询详情')
    @api.marshal_with(sensoralarms_model)
    @api.response(200,'ok')
    @api.response(404,'Not Found')
    def get(self,sensoralarmid):
        sensoralarm=SensorAlarm.query.get_or_404(sensoralarmid)
        if sensoralarm.sensor not in[i.sensor for i in g.user.home]:
            return '权限不足',301
        else: return sensoralarm,200

    @api.doc('删除报警记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require([ ])
    @api.response(200,'ok')
    def delete(self,sensoralarmid):
        sensoralarm = SensorAlarm.query.get_or_404(sensoralarmid)
        db.session.delete(sensoralarm)
        db.session.commit()
        return None,200
    @api.doc('更新传感器的报警记录/报警确认')
    @api.expect(sensoralarms_parser1,validate=True)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','119user','admin','superadmin'])
    @api.response(200, 'ok')
    def put(self,sensoralarmid):
        sensoralarm=SensorAlarm.query.get_or_404(sensoralarmid)
        if 'homeuser'in [i.name for i in g .user.role] and len(g.user.roles.all())<2:
            home=Home.query.get_or_404( sensoralarm.sensor.home_id)
            if home.admin_user_id==g.user.id:
                sensoralarm.is_confirm=True
                db.session.commit()
                return None,200
            else: return '权限不足',301
        else:
            sensoralarm.is_confirm=True
            db.session.commit()
            return None, 200







