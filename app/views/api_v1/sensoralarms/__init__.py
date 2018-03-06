from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import SensorAlarm
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms.parser import sensoralarms_parser

api=Namespace('Sensoralarms',description='传感器报警相关操作')
from .models import *
@api.route('/')
class SensorAlarmsView(Resource):
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
    @api.expect(sensoralarms_parser)
    @api.response(200,'ok')
    def post(self):
     args=sensoralarms_parser.parse_args()
     sensoralarm=SensorAlarm(**args)
     db.session.add(sensoralarm)
     db.session.commit()
     return None,200
@api.route('/<sensoralarmid>')####根据传感器id查询传感器报警历史记录????
class SensorAlarmView(Resource):
    @api.doc('根据报id查询详情')
    @api.marshal_with(sensoralarms_model)
    @api.response(200,'ok')
    @api.response(404,'Not Found')
    def get(self,sensoralarmid):
        sensoralarm=SensorAlarm.query.get_or_404(sensoralarmid)
        return sensoralarm,200
    ######@api.doc('根据报警id发送疏散信息')
    @api.doc('删除报警记录')
    @api.response(200,'ok')
    def delete(self,sensoralarmid):
        sensoralarm = SensorAlarm.query.get_or_404(sensoralarmid)
        db.session.delete(sensoralarm)
        db.session.commit()
        return None,200



