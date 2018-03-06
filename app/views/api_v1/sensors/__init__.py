from flask_restplus import Namespace
from flask_restplus import  Resource
from app.ext import db
from app.models import Facility, Sensor
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms import sensoralarms_model
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1

api = Namespace('Sensors', description='传感器相关接口')
from .model import *
@api.doc('')
@api.route('/')
class SensorsView(Resource):
    @page_format(code=0,msg='ok')
    @api.marshal_with(sensor_model, as_list=True)
    @api.doc('查询传感器列表')
    @api.marshal_with(sensor_model)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200, 'ok')
    @page_range()
    def get(self):
        list = Sensor.query
        return list

    @api.doc('新增传感器')
    #@api.marshal_with(sensor_model)
    @api.response(200, 'ok')
    @api.expect(sensor_parser,validate=True)
    def post(self):
        args=sensor_parser.parse_args()
        sensor=Sensor(**args)
        db.session.add(sensor)
        db.session.commit()
        return None,200
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
            sensor1=Sensor.query.get_or_404(sensorid)
            args=sensor_parser.parse_args()

            if args['gateway_id']:
                sensor1.gateway_id=args.get('gateway_id')
            else:pass
            if args['sensor_type']:
                 sensor1.sensor_type=args.get('sensor_type')
            else:pass
            if args['sensor_place']:
                sensor1.sensor_place=args.get('sensor_place')
            else:pass
            if args['start_time']:
                sensor1.start_time=args.get('start_time')
            else:pass
            if args['end_time']:
                sensor1.end_time=args.get('end_time')
            else:pass
            if args['max_value']:
                sensor1.max_value=args.get('max_value')
            else:pass

            db.session.commit()
            return None,200


@api.route('/<sensorid>/sensoralarm')
class SensorAlarmsView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询传感器的报警历史')
    @api.marshal_with(sensoralarms_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200,'ok')
    @page_range()
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        return sensor.alarms_history,200


