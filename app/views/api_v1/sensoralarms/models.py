from flask_restplus import fields

from app.views.api_v1.sensoralarms import api

sensoralarms_model=api.model('Sensoralarms',{
    'id':fields.String,
    'sensor_id':fields.String,
    'alarm_object':fields.String,
    'alarm_value':fields.Float,
    'alarm_time':fields.DateTime,
    'confirm_time':fields.DateTime,
    'is_timeout':fields.Boolean,
    'user_id':fields.String,
    'is_confirm':fields.Boolean



})