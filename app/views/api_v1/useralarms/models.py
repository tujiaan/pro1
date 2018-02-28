from flask_restplus import fields

from app.views.api_v1.useralarms import api

useralarmrecord_model=api.model('UserAlarmRecord',{
    'id':fields.String,
    'type':fields.Integer,
    'content':fields.String,
    'user_id':fields.String,
    'community_id':fields.String

})