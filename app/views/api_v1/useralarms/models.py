from flask_restplus import fields

from app.views.api_v1.useralarms import api

useralarmrecord_model=api.model('UserAlarmRecord',{
    'useralarmrecord_id':fields.String,
    'useralarmrecord_type':fields.Integer,
    'useralarmrecord_content':fields.String,
    'useralarmrecord_time':fields.datetime,
    'useralarmrecord_if_confirm':fields.Boolean,
    'community_id':fields.String,
    'community_name':fields.String,
    'home_id':fields.String,
    'detail_address':fields.String,
    'user_id':fields.String,
    'user_name':fields.String,
    'contract_tel':fields.String


})