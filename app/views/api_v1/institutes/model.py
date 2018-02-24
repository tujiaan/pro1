from flask_restplus import Model, fields
from . import api
import base64
#from ..facilities.models  import *
from ..facilities.models import  facility_model
ins_model = api.model('InsModel', {
    'id': fields.String,
    'ins_picture':fields.String(attribute=lambda x: base64.b64encode(x.ins_picture))
})
ins_model = api.model('InsModel', {
    'id': fields.String,
    'type': fields.String,
    'name': fields.String,
    'ins_picture':fields.Nested(ins_model),
    'ins_address': fields.String,
    'note': fields.String,
    'admin_user_id': fields.String,
    'longitude': fields.Float,
    'latitude':fields.Float,
    'link_facility':fields.List(fields.Nested(facility_model))
})
