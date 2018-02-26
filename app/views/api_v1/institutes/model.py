from flask_restplus import Model, fields
from . import api

facility_model = api.model('FacilityModel', {
    'id': fields.String,
    'facility_id':fields.String,
    'ins_id':fields.String,
    'count':fields.Integer,
    #'expire_time':fields.DateTime,
    'expire_time': fields.String

})

