from flask_restplus import fields

from . import api
homeuser_model= api.model('UserHomeModel', {
    'user_id': fields.String,
    'home_id':fields.String,
    'if_confirm':fields.Boolean,
    'apply_time': fields.DateTime,
    'confirm_time':fields.DateTime
})
