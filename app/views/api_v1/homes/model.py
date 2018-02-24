from flask_restplus import Model, fields
from . import api

home_model = api.model('HomeModel', {
    'id': fields.String,
    'name': fields.String,
    'community_id': fields.String,
    'admin_user_id': fields.String,
    'detail_address': fields.String,
    'link_name': fields.String,
    'telephone': fields.String,
    'longtitude': fields.Float,
    'latitude':fields.Float,
    'alternate_phone':fields.String
})
