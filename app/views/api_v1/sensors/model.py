from flask_restplus import Model, fields
from . import api

sensor_model = api.model('SensorModel', {
    'id': fields.String,
    'gateway_id': fields.String,
    'sensor_type': fields.Integer,
    'sensor_place': fields.String,
    'home_id':fields.String,
    'start_time':fields.DateTime,
    'end_time':fields.DateTime,
    'max_value':fields.Float,
    'sensor_switch':fields.String
})
