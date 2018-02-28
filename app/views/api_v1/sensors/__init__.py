from flask_restplus import Namespace
from flask_restplus import  Resource
from app.ext import db
from app.models import Facility, Sensor
from app.utils.tools.page_range import page_range
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1

api = Namespace('Sensors', description='传感器相关接口')
from .model import *
@api.doc('')
@api.route('/')
class SensorsView(Resource):
    @api.marshal_with(sensor_model, as_list=True)
    @api.doc('查询传感器列表')
    @api.marshal_with(sensor_model)
    @api.doc(params={'from': '开始', 'count': '数量'})
    @api.response(200, 'ok')
    @page_range()
    def get(self):
        list = Sensor.query
        return list

    @api.doc('新增传感器')
    #@api.marshal_with(sensor_model)
    @api.response(200, 'ok')
    @api.expect(sensor_parser)
    def post(self):
        args=sensor_parser.parse_args()
        sensor=Sensor(**args)
        db.session.add(sensor)
        db.session.commit()
        return None,200 ###需要先设置home表才可以
    @api.doc('')
    @api.route('/<sensorid>')
    class SensorsView(Resource):
        @api.doc('获取传感器详情')
        @api.marshal_with(sensor_model)
        @api.response(200, 'ok')
        def get(self,sensorid):
            sensor=Sensor.query.get_or_404(sensorid)
            return sensor,200

        @api.doc('删除传感器')
        @api.response(200, 'ok')
        def delete(self, sensorid):
             sensor=Sensor.query.filter_by(id=sensorid).first()
             db.session.delete(sensor)
             db.session.commit()
             return None ,200

        @api.doc('更新传感器信息')
        #@api.marshal_with(sensor_model)
        @api.response(200, 'ok')
        @api.expect(sensor_parser1)
        def put(self,sensorid):
            sensor1=Sensor.query.filter_by(id=sensorid).first()
            args=sensor_parser.parse_args()

            if args.get('gateway_id'):
                sensor1.gateway_id=args.get('gateway_id')
            if args.get('sensor_type'):
                 sensor1.sensor_type=args.get('sensor_type')
            if args.get('sensor_place'):
                sensor1.sensor_place=args.get('sensor_place')
            db.session.commit()
            return None,200
