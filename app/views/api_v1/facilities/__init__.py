from flask_restplus import Namespace, Resource
from app.models import Facility



api = Namespace('Facilities', description='设备相关接口')
from .models import *
@api.doc("")
class FacilitesView(Resource):
    @api.doc("查询设施列表")
    @api.marshal_with(facility_model,as_list=True)
    @api.response('ok',200)
    def get(self):
       list=Facility.queery.limit(5).offset(0).all()
       return list,200
