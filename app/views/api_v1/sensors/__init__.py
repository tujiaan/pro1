import dateutil
from flask import g, request
from flask_restplus import Namespace
from flask_restplus import  Resource
from sqlalchemy import and_

from app.ext import db
from app.models import Facility, Sensor, Home, SensorAlarm, SensorHistory, HomeUser, UserRole, Role, User, SensorTime
from app.utils.auth.auth import role_require
#from app.utils.myutil.url import getResponse
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.sensoralarms import sensoralarms_model
from app.views.api_v1.sensorhistory import sensorhistory_model
from app.views.api_v1.sensors.parsers import sensor_parser, sensor_parser1, sensor_parser2, sensortime_parser
import datetime
import time

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
        page=int(request.args.get('page',1))
        limit=int(request.args.get('limit',10))
        sensor_type=request.args.get('sensor_type',None)
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).all()
        home = Home.query.filter(Home.id.in_(i.home_id for i in homeuser)).all()
        if g.role.name=='homeuser':
            if sensor_type!=None:
                query = db.session.query(Sensor,Home).join(Home,Home.gateway_id==Sensor.gateway_id).\
                    filter(Sensor.sensor_type==sensor_type).filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
            else:  query = db.session.query(Sensor,Home).join(Home,Home.gateway_id==Sensor.gateway_id).\
                  filter(Sensor.gateway_id.in_(i.gateway_id for i in home)).order_by(Sensor.id)\
                    .offset((int(page) - 1) * limit).limit(limit)
        else:
            if sensor_type!=None:
                query = db.session.query(Sensor,Home).join(Home,Home.gateway_id==Sensor.gateway_id).\
                    filter(Sensor.sensor_type==sensor_type).order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
            else:     query = db.session.query(Sensor,Home).join(Home,Home.gateway_id==Sensor.gateway_id).\
                   order_by(Sensor.id).offset((int(page) - 1) * limit).limit(limit)
        total=Sensor.query.count()
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
        # url = 'http://119.28.155.88:8080/data/api/v1/dataPoint/53/list'
        # result = getResponse(url)
        # list = result.get('data')
        # for i in list:
        #     name = i.get('name')
        #     str = name.split('-')
        #     sensor= Sensor(id=str[1],sensor_type=str[0])
        #     db.session.add(sensor)
        # db.session.commit()##########################################待修改
        return None,200

@api.route('/<sensorid>/')
class SensorsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'propertyuser', 'stationuser', '119user', 'admin', 'superadmin'])
    @api.doc('获取传感器详情')
    @api.response(200, 'ok')
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id).first()
        user=User.query.get_or_404(home.admin_user_id)
        homeuser= HomeUser.query.filter(HomeUser.home_id==home.id).all()
        query=db.session.query(Sensor,SensorHistory,Home).join(SensorHistory,Sensor.id==SensorHistory.sensor_id).\
            join(Home,Sensor.gateway_id==Home.gateway_id).filter(Sensor.id==sensorid)
        total=query.count()
        _=[]
        for i in [query.first()]:
            __={}
            __['sensor_id']=i[0].id
            __['sensor_type']=i[0].sensor_type
            __['max_value']=i[0].max_value
            __['set_type']=i[0].set_type
            __['sensor_place']=i[0].sensor_place
            __['sensor_state']=tuple(SensorHistoryView.get(self,i[0].id))[0].get('sensor_state')
            __['gateway_id']=i[0].gateway_id
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
                if g.user.id not in [i.user_id for i in homeuser]:
                    return '权限不足',201
                else: return result,200
            elif g.role.name in[ 'propertyuser', 'stationuser', '119user']:
                return '权限不足', 201
            else:return result,200
        else:
            if g.role.name == 'homeuser':
                if g.user.id not in [i.user_id for i in homeuser]:
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
        home=Home.query.filter(Home.gateway_id==sensor1.gateway_id).first()
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
        if args['max_value']:
            sensor1.max_value=args.get('max_value')
            if sensor1.type==3:
                sensor1.set_type='1'
            else:pass
        else:pass
        if args['set_type']:
            sensor1.set_type=args['set_type']
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
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id).first()
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
        sensor=Sensor.query.get_or_404(sensorid)
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id).first()
        sensorhistory=SensorHistory.query.filter(SensorHistory.sensor_id==sensorid).order_by(SensorHistory.time.desc()).first()
        if g.role.name=='homeuser':
            if g.user.id in [i.user_id for i in (HomeUser.query.filter(HomeUser.home_id==home.id))]:
                return  sensorhistory, 200
            else:return '权限不足',201

        else:
            return sensorhistory, 200


@api.route('/<sensorid>/sensortime')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('查询特定传感器定时')
    @api.marshal_with(sensortime_model,as_list=True)
    def get(self,sensorid):
        sensor=Sensor.query.get_or_404(sensorid)
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id).first()
        homeuser=HomeUser.query.filter(HomeUser.home_id==home.id).all()
        sensortime=SensorTime.query.filter(SensorTime.sensor_id==sensorid).all()
        if g.user.id in [i.user_id for i in homeuser]:
            return sensortime,200
        else:return '权限不足',201


@api.route('/<sensortimeid>/sensortime')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('删除特定传感器定时')
    def delete(self,sensortimeid):
        sensortime = SensorTime.query.get_or_404(sensortimeid)
        sensor=Sensor.query.get_or_404(sensortime.sensorid)
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id).first()
        db.session.delete(sensortime)
        if g.user.id==home.admin_user_id:
            db.session.commit()
            return '删除成功',200
        else:return '权限不足',201

    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.doc('开启定时传感器')
    @api.expect(sensortime_parser)
    def put(self, sensortimeid):
        sensortime=SensorTime.query.get_or_404(sensortimeid)
        sensor=Sensor.query.get_or_404(sensortime.sensor_id)
        home=Home.query.filter(Home.gateway_id==sensor.gateway_id)
        args=sensortime_parser.parse_args()
        if args['switch_on']:
            sensortime.switch_on=args['switch_on']
        else:pass
        if g.user.id==home.admin_user_id:
            db.session.commit()
            return '开启成功',200
        else: return '权限不足',201


@api.route('/sensortime/')
class SensorTimeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','superadmin'])
    @api.doc('新增传感器定时')
    @api.expect(sensor_parser2)
    def post(self):
        args = sensor_parser2.parse_args()
        sensortime = SensorTime()
        if args['sensor_id']:
            sensor = Sensor.query.get_or_404(args['sensor_id'])
            home = Home.query.filter(Home.gateway_id == sensor.gateway_id).first()
            sensortime.sensor_id=args['sensor_id']
        if args['start_time']:
            sensortime.start_time = args['start_time']
        else:pass
        if args['end_time']:
            sensortime.end_time = args['end_time']
        else:pass
        db.session.add(sensortime)
        if g.role.name == 'homeuser':
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return '添加成功', 200
            else:
                return '权限不足', 201
        else:
            db.session.commit()
            # return '添加成功', 200
            return {'start_time':str(sensortime.start_time),'type':str(type(sensortime.start_time))}, 200


@api.route('/<start_time>/<end_time>/<sensorid>/maxvalue')
class SensorTimeViews(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser','superadmin'])
    @api.doc('智能电流设定')
    def get(self, start_time, end_time, sensorid):
        sensor = Sensor.query.get_or_404(sensorid)
        datetime1 = datetime.date.today().strftime('%Y-%m-%d')
        start_time1 = datetime.datetime.strptime(datetime1 + "\t " + start_time+":00", "%Y-%m-%d %H:%M:%S")
        end_time1 = datetime.datetime.strptime(datetime1 + "\t" + end_time+":00", "%Y-%m-%d %H:%M:%S")
        sensorhistory = SensorHistory.query.filter(SensorHistory.sensor_id == sensor.sensor_id).\
            filter(SensorHistory.time.between(start_time1, end_time1)).order_by(SensorHistory.sensor_value.desc()).\
            first()
        sensor.max_value = sensorhistory.sensor_value
        sensor.set_type = '2'
        db.session.commit()
        result = {
            'start_time': start_time,
            'end_time': end_time,
            'max_value': sensorhistory.sensor_value
            }
        return result, 200








