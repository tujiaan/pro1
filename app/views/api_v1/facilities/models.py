from flask_restplus import Model, fields
from app.views.api_v1.facilities import api
import base64

facility_model = api.model('FacilityModel', {
    'id': fields.String,
    'facility_id':fields.String,
    'ins_id':fields.String,
    'count':fields.Integer,
    'expire_time':fields.DateTime,


})
facility_data_picture_model=api.model('FacilityPictureModel',{
         'id':fields.String,
         'facility_picture':fields.String(attribute=lambda x :base64.b64encode(x.facility_picture))
})
facility_data_model = api.model('FacilityDataModel', {
    'id': fields.String,
    'facility_name':fields.String,
    'facility_picture':fields.Nested(facility_data_picture_model)

})