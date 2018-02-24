from flask_restplus import Model, fields
from . import api
from ..institutes.model import ins_model
facility_model = api.model('FacilityModel', {
    'id': fields.String,
    'facility_id':fields.String,
    'ins_id':fields.String,
    'count':fields.Integer,
    'expire_time':fields.DateTime,


})
