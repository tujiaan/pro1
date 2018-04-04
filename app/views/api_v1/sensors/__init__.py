from flask import g, request
from flask_restplus import Namespace
from flask_restplus import  Resource
from app.ext import db
from app.models import Facility, Sensor, Home, SensorAlarm, SensorHistory, HomeUser, UserRole, Role, User
from app.utils.auth.auth import role_require
from app.utils.myutil.url import getResponse
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms import sensoralarms_model
from app.views.api_v1.sensorhistory import sensorhistory_model
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1

api = Namespace('Sensors', description='传感器相关接口')
from .model import *
@api.route('/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require([ 'homeuser','admin', 'superadmin'])
    @api.doc('查询传感器列表')
    @api.doc(params={'page': '页数', 'limit': '数量','sensor_type':'类型'})
    @api.response(200, 'ok')
    def get(self):
        page=request.args.get('page',1)
        limit=request.args.get('limit',10)
        sensor_type=request.args.get('sensor_type',None)
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        if g.role.name=='homeuser':
            if sensor_type!=None:
                query = db.session.query(Sensor,Home).join(Home,Home.id==Sensor.home_id).\
                    filter(Sensor.sensor_type==sensor_type).filter(Sensor.home_id.in_(i.id for i in home)).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
            else:  query = db.session.query(Sensor,Home).join(Home,Home.id==Sensor.home_id).\
                  filter(Sensor.home_id.in_(i.id for i in home)).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
        else:
            if sensor_type!=None:
                query = db.session.query(Sensor,Home).join(Home,Home.id==Sensor.home_id).\
                    filter(Sensor.sensor_type==sensor_type).order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
            else:     query = db.session.query(Sensor,Home).join(Home,Home.id==Sensor.home_id).\
                   order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
        total=query.count()
        _=[]
        for i in query.all():
            __={}
            __['sensor_id']=i[0].id
            __['sensor_type']=i[0].sensor_type
            __['sensor_place']=i[0].sensor_place
            __['gateway_id']=i[0].gateway_id
            __['home_id']=i[1].id
            __['home_name']=i[1].name
            _.append(__)
        result={
             'code':0,
             'msg':'200',
             'count':total,
             'data':_
         }
        return result,200


    @api.doc('新增传感器')
    @api.header('jwt', 'JSON Web Token')
    @role_require([])
    @api.response(200, 'ok')
    @api.expect(sensor_parser,validate=True)
    def post(self):
        url = 'http://119.28.155.88:8080/data/api/v1/dataPoint/53/list'
        result = getResponse(url)
        list = result.get('data')
        for i in list:
            name = i.get('name')
            str = name.split('-')
            sensor= Sensor(id=str[1],sensor_type=str[0])
            db.session.add(sensor)
        db.session.commit()##########################################待修改
        return None,200

@api.route('/<sensorid>/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('获取传感器详情')
    @api.response(200, 'ok')
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        user=User.query.get_or_404(sensor.home.admin_user_id)
        homeuser= HomeUser.query.filter(HomeUser.home_id==sensor.home_id).all()
        query=db.session.query(Sensor,SensorHistory,Home).join(SensorHistory,Sensor.id==SensorHistory.sensor_id).\
            join(Home,Sensor.home_id==Home.id).filter(Sensor.id==sensorid)
        total=query.count()
        _=[]
        for i in [query.first()]:
            __={}
            __['sensor_id']=i[0].id
            __['sensor_type']=i[0].sensor_type
            __['sensor_place']=i[0].sensor_place
            __['sensor_state']=tuple(SensorHistoryView.get(self,i[0].id))[0].get('sensor_state')
            __['home_id']=i[2].id
            __['home_name']=i[2].name
            _.append(__)
        result = {
            'code': 0,
            'msg': 'ok',
            'count': total,
            'data': _
        }
        if user.sensor_visable==False:
            if g.role.name=='homeuser':
                if g.user.id not in homeuser:
                    return '权限不足',201
                else: return result,200
            elif g.role.name in[ 'propertyuser', 'stationuser', '119user']:
                return '权限不足', 201
            else:return result,200
        else:
            if g.role.name == 'homeuser':
                if g.user.id not in homeuser:
                    return '权限不足', 201
                else:return result,200
            else:
                return result,200





    @api.doc('更新传感器信息')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.response(200, 'ok')
    @api.expect(sensor_parser1)
    def put(self,sensorid):
        sensor1=Sensor.query.get_or_404(sensorid)
        home=Home.query.filter(Home.id==sensor1.home_id).first()
        args=sensor_parser1.parse_args()
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
        if args['sensor_switch']:
            sensor1.sensor_switch=True
        else:pass
        if g.user.id==home.admin_user_id:
            db.session.commit()
            return None,200
        else:return '权限不足',301


@api.route('/<sensorid>/sensoralarm')
class SensorAlarmsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','propertyuser','stationuser','119user''admin','superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询传感器的报警历史')
    @api.marshal_with(sensoralarms_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200,'ok')
    @page_range()
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        home=sensor.home
        homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
        sensoralarm=SensorAlarm.query.filter(SensorAlarm.sensor_id==sensorid)
        if g.role.name=='homeuser':
            if g.user.id in [i.user_id for i in homeuser ] :
              return sensoralarm,200
            else:  pass
        elif g.role.name in ['119user','stationuser','propertyuser']:
            return  sensoralarm.filter(SensorAlarm.is_confirm==False).filter( SensorAlarm.is_timeout==True).\
                   filter(SensorAlarm.sensor_id==sensorid)
        else:
            return sensoralarm,200

@api.route('/<sensorid>/sensorhistory')
class SensorHistoryView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'insuser', '119user''admin', 'superadmin'])
    @api.doc('查询最近的一条传感器历史')
    @api.marshal_with(sensorhistory_model)
    @api.response(200,'ok')
    def get(self,sensorid):
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        sensor=Sensor.query.get_or_404(sensorid)
        home=sensor.home
        sensorhistory=SensorHistory.query.filter(SensorHistory.sensor_id==sensorid).order_by(SensorHistory.time.desc()).first()
        if g.role.name=='homeuser':
            if g.user.id in [i.user_id for i in (HomeUser.query.filter(HomeUser.home_id==home.id))]:
                return  sensorhistory, 200
            else:return '权限不足',201

        else:
            return sensorhistory, 200





