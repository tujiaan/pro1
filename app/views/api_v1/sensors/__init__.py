from flask import g
from flask_restplus import Namespace
from flask_restplus import  Resource
from app.ext import db
from app.models import Facility, Sensor, Home, SensorAlarm
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms import sensoralarms_model
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1

api = Namespace('Sensors', description='传感器相关接口')
from .model import *
@api.doc('')
@api.route('/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require([ 'admin', 'superadmin'])
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
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
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
        @api.header('jwt', 'JSON Web Token')
        @role_require(['homeuser', '119user', 'insuser' 'admin', 'superadmin'])
        @api.doc('获取传感器详情')
        @api.marshal_with(sensor_model)
        @api.response(200, 'ok')
        def get(self,sensorid):
            sensor=Sensor.query.get_or_404(sensorid)
            if 'homeuser'in [i.name for i in g.user.role]:
                if sensor not in[i.sensor for i in g.user.home]:
                    return '权限不足',301
                else:return sensor,200
            else: return sensor,200

        @api.doc('删除传感器')######?????????????????????????????????????????????
        @api.response(200, 'ok')
        @api.header('jwt', 'JSON Web Token')
        @role_require([])
        def delete(self, sensorid):

             sensor=Sensor.query.get_or_404(sensorid)
             db.session.delete(sensor)
             db.session.commit()
             return None ,200

        @api.doc('更新传感器信息')
        @api.header('jwt', 'JSON Web Token')
        @role_require(['homeuser'])
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
            if args['home_id']:
                sensor1.home_id = args.get('home_id')
            else:
                pass
            if args['start_time']:
                sensor1.start_time=args.get('start_time')
            else:pass
            if args['end_time']:
                sensor1.end_time=args.get('end_time')
            else:pass
            if args['max_value']:
                sensor1.max_value=args.get('max_value')
            else:pass
            if sensor1.home_id not in[i.id for i in g.user.home]:

                db.session.commit()
                return None,200
            else:return '权限不足',301


@api.route('/<sensorid>/sensoralarm')
class SensorAlarmsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','insuser','119user''admin','superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询传感器的报警历史')
    @api.marshal_with(sensoralarms_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200,'ok')
    @page_range()
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        if 'homeuser'in [i.name for i in g.user.role]:
            if sensor not in [i.sensor for i in g.user.home]:
                return '权限不足',301
        elif ('insuser'or '119user')in [i.name for i in g.user.role]:
           ins=(Home.query.get_or_404(sensor.home_id)).ins
           if g.user.id==ins.admin_user_id :
               return SensorAlarm.query.filter(SensorAlarm.is_confirm==False and SensorAlarm.is_timeout==True)
           else: return '权限不足',301

        else: return SensorAlarm.query,200


