from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Facility, FacilityData,Knowledge
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.facilities.parser import facility_parser, facility_parser1, f_parser, f1_parser

api = Namespace('Facilities', description='设备相关接口')

from .models import *


@api.route('/')
class FacilitiesDataView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询设施列表')

    @api.marshal_with(facility_data_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list = FacilityData.query
        return list, 200
    @api.doc('新增设施')
    @api.expect(f_parser)
    def post(self):
        args=f_parser.parse_args()
        facility_data=FacilityData()
        facility_data.facility_name=args['facility_name']
        p=args['facility_picture']
        facility_data.facility_picture=p.read()
        db.session.add(facility_data)
        db.session.commit()
        return None,200

@api.route('/<facilityid>/')
class FacilityDataView(Resource):
    @api.doc('根据设施id查询详情')
    @api.marshal_with(facility_data_model)
    @api.response(200,'ok')
    def get(self,facilityid):
        facility_data=FacilityData.query.filter_by(id=facilityid).first()
        return facility_data,200
    @api.doc('更新设施详情')
    @api.expect(f1_parser)
    @api.response(200,'ok')
    def put(self,facilityid):
        facility_data1=FacilityData.query.filter_by(id=facilityid).first()
        args=f1_parser.parse_args()
        facility_data = FacilityData()
        facility_data.facility_name = args['facility_name']
        p = args['facility_picture']
        if p :
         facility_data.facility_picture = p.read()
        if facility_data.facility_name is not None:
            facility_data1.facility_name=facility_data.facility_name
        else:pass
        if facility_data.facility_picture is not None:
            facility_data1.facility_picture=  facility_data.facility_picture
        else:pass
        db.session.commit()
        return None,200

    @api.doc('删除设施')
    @api.response(200, 'ok')
    def delete(self,facilityid):
        facility_data = FacilityData.query.get_or_404(facilityid)
        db.session.delete(facility_data)
        db.session.commit()
        return None,200





@api.route('/facility-ins/')
class FacilitesInsView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc("查询设施关联机构列表")
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(facility_model,as_list=True)
    @api.response(200,'ok')
    @page_range()
    def get(self):
       list=Facility.query
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

@api.route('/facility-ins/<facilityid>/')
class FacilitesView(Resource):
        @api.doc('删除机构设施关联')##ok
        @api.response(200, 'ok')
        def delete(self,facilityid):
            facility=Facility.query.filter_by(facility_id=facilityid).first()
            db.session.delete(facility)
            db.session.commit()
            return None,200
        @api.doc('更新机构设施关联')#ok
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


@api.route('/<facilityid>/knowledges/')
class FacilityKnowledgesView(Resource):
    @page_format(code=0,msg='ok')
    @api.doc('查询设施的知识')
    @api.marshal_with( knowledges_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @ page_range()
    @api.response(200,'ok')
    def get(self,facilityid):
        facility=Facility.query.get_or_404(facilityid)
        return facility.knowledges.all(),200

@api.route('/<facilityid>/knowledges/<knowledgeid>/')
class FacilityKnowledgeView(Resource):

    @api.doc('给设施绑定知识')
    @api.response(200,'ok')
    @api.response(404,'Not Found')
    def post(self,facilityid,knowledgeid):
        try:
            facility = Facility.query.get_or_404(facilityid)

            knowledge = Knowledge.query.get_or_404(knowledgeid)

            facility.knowledges.append(knowledge)

            db.session.commit()
            return '绑定成功', 200
        except: return '已经绑定'

    @api.doc('解除设施绑定知识')
    @api.response(200, 'ok')
    @api.response(404, 'Not Found')
    def delete(self, facilityid, knowledgeid):
        try:
            facility = Facility.query.get_or_404(facilityid)
            knowledge = Knowledge.query.get_or_404(knowledgeid)

            facility.knowledges.remove(knowledge)
            db.session.commit()
            return None,200
        except:
          return'已经解除'









