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
