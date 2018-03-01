import base64
from flask_restplus import  fields
from . import api


institute_picture_model=api.model('InstitutePictureModel', {
    'id':fields.String,
    'ins_picture':fields.String(attribute=lambda x: base64.b64encode(x).decode() if x else None)
})
institute_model = api.model('InstituteModel', {
    'id': fields.String,
    'type':fields.String,
    'name':fields.String,
    'ins_address': fields.String,
    'ins_picture': fields.Nested(institute_picture_model),
    'admin_user_id': fields.String,
    'note': fields.String,
    'longitude': fields.Float,
    'latitude': fields.Float

})

