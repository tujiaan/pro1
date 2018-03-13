from flask_restplus import fields

from . import api


user_model = api.model('UserModel', {
    'id': fields.String,
    'disabled': fields.Boolean,
    'contract_tel': fields.String,
    'username': fields.String,
    'email': fields.String,
    'createTime': fields.DateTime,
    'lastTime': fields.DateTime,
    'real_name': fields.String
})
#from app.views.api_v1.homes import api

home_model = api.model('HomeModel', {
    'id': fields.String,
    'name': fields.String,
    'community_id': fields.String,

    'detail_address': fields.String,
    'link_name': fields.String,
    'telephone': fields.String,
    'longitude': fields.Float,
    'latitude':fields.Float,
    'alternate_phone':fields.String
})

