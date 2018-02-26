from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Facility, FacilityData
from app.utils.tools.page_range import page_range
from app.views.api_v1.facilities.parser import facility_parser, facility_parser1

api = Namespace('Facilities', description='设备相关接口')

from .models import *


@api.route('/')
class FacilitiesDataView(Resource):
    @api.doc('查询设施列表')
    @api.marshal_with(facility_data_model)
    @api.marshal_with(facility_data_model, as_list=True)
    @api.doc(params={'from': '开始', 'count': '数量'})
    @page_range()
    def get(self):
        list = FacilityData.query
        return None, 200

@api.route('/facility-ins/')
class FacilitesInsView(Resource):
    @api.doc("查询设施关联列表")
    @api.doc(params={'from':'开始','count':'数量'})
    @api.marshal_with(facility_model,as_list=True)
    @api.response(200,'ok')
    @page_range()
    def get(self):
       list=FacilityData.query
       return list,200

    @api.doc('新增设施机构关联')
    @api.response(200,'ok')
    @api.expect(facility_parser)
    def post(self):
        args=facility_parser.parse_args()
        facility=Facility(**args)
        db.session.add(facility)
        db.session.commit()
        return  None,200

@api.route('/facility-ins/<facilityid>')
class FacilitesView(Resource):
        @api.doc('删除机构设施关联')
        @api.response(200, 'ok')
        def delete(self,facilityid):
            facility=Facility.query.filter_by(facility_id=facilityid).first()
            db.session.delete(facility)
            db.session.commit()
            return None,200
        @api.doc('更新机构设施关联')
        @api.response(200,'ok')
        @api.expect(facility_parser1)
        def put(self,facilityid):
            args=facility_parser1.parse_args()
            facility=Facility.query.filter_by(facility_id=facilityid).first()
            if args.get('ins_id'):
                facility.ins_id=args.get('ins_id')
            else:pass
            if args.get('count'):
                facility.count= args.get('count')
            else:pass
            if args.get('expire_time'):
                facility.expire_time=args.get('expire_time')
            else:pass
            db.session.commit()
            return None,200





