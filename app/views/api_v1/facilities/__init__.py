from flask import g, request
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Facility, FacilityIns, Knowledge, UserRole, Role, Ins
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.facilities.parser import facility_parser, facility_parser1, f_parser, f1_parser

api = Namespace('Facilities', description='设备相关接口')

from .models import *


@api.route('/')
class FacilitiesInsView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.doc('查询设施列表')
    @api.marshal_with(facility_data_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list = Facility.query
        return list, 200


    @api.doc('新增设施')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','superadmin'])
    @api.expect(f_parser)
    def post(self):
        args=f_parser.parse_args()
        facility_data=Facility()
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
        facility_data=Facility.query.get_or_404(facilityid)
        return facility_data,200

    @api.doc('更新设施详情')
    @api.expect(f1_parser)
    @api.response(200,'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin','propertyuser','stationuser'])
    def put(self,facilityid):
        facility = Facility.query.get_or_404(facilityid)
        facilityins=FacilityIns.query.filter(FacilityIns.facility_id==facilityid).first()
        ins=Ins.query.filter(Ins.id==facilityins.ins_id).first()
        args = facility_parser1.parse_args()
        if args['facility_name']:
            facility.facility_name=args['facility_name']
        else:pass
        if args['facility_picture']:
            facility.facility_picture=args['facility_picture']
        else:pass
        if g.role.name not in['propertyuser','stationuser']:
           db.session.commit()
           return'修改成功',200
        elif g.user.id==ins.admin_user_id:
                db.session.commit()
                return '修改成功', 200
        else: return'权限不足',201



    @api.doc('删除设施')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self,facilityid):
        facility = Facility.query.get_or_404(facilityid)
        facilityins=FacilityIns.query.filter(FacilityIns.facility_id==facilityid).first()
        knowledge=facility.knowledge
        db.session.delete(facilityins)
        db.session.commit()
        for i in knowledge:
            FacilityKnowledgeView.delete(self,facilityid,i.id)
            db.session.commit()
        db.session.delete(facility)
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
       list=FacilityIns.query
       return list,200


    @api.doc('新增设施机构关联')
    @api.response(200,'ok')
    @api.expect(facility_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def post(self):
        args=facility_parser.parse_args()
        facilityins=FacilityIns(**args)
        try:
            ins=Ins.query.get_or_404(facilityins.ins_id)
            facility=Facility.query.get_or_404(facilityins.facility_id)
            db.session.add(facilityins)
            db.session.commit()################################################可能有问题###################
            return  None,200
        except:return '信息有误',201
@api.route('/facility-ins/<insid>')
class FacilitesInsView(Resource):
    @api.doc("查询设施机构关联设施列表")
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.response(200,'ok')
    def get(self,insid):
        page=request.args.get('page',1)
        limit=request.args.get('limit',10)
        query=FacilityIns.query.filter(FacilityIns.ins_id==insid).offset((int(page) - 1) * limit).limit(limit)
        total=query.count()
        _=[]
        for i in query.all():
            __={}
            __['id']=i.id
            __['ins_id']=i.ins_id
            __['ins_name']=Ins.query.get_or_404(i.ins_id).name
            __['facility_id']=i.facility_id
            __['count']=i.count
            __['expire_time']=str(i.expire_time)
            _.append(__)

        result={
            'code':0,
            'msg':'ok',
            'result':_
        }
        return result,200



@api.route('/facility-ins/<facilityid>/')
class FacilitesView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['propertyuser','stationuser','admin', 'superadmin'])
    @api.doc('删除机构设施关联')
    @api.response(200, 'ok')
    def delete(self,facilityid):
        facilityins=FacilityIns.query.filter(FacilityIns.facility_id==facilityid).first()
        ins=Ins.query.filter(Ins.id==facilityins.ins_id).first()
        db.session.delete(facilityins)
        if g.role.name not in ['propertyuser','stationuser']:
            db.session.commit()
            return None,200
        elif g.user.id==ins.admin_user_id:
            db.session.commit()
            return'删除成功',200
        else:return'权限不足',201




    @api.doc('更新机构设施关联')
    @api.response(200,'ok')
    @api.expect(facility_parser1)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin','propertyuser','stationuser'])
    def put(self,facilityid):
        args=facility_parser1.parse_args()
        facilityins=FacilityIns.query.filter(FacilityIns.facility_id==facilityid).first()
        if args.get('ins_id'):
            facilityins.ins_id=args.get('ins_id')
        else:pass
        if args.get('count'):
            facilityins.count= args.get('count')
        else:pass
        if args.get('expire_time'):
            facilityins.expire_time=args.get('expire_time')
        else:pass
       ##############################有问题########################



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
        return facility.knowledges,200

@api.route('/<facilityid>/knowledges/<knowledgeid>/')
class FacilityKnowledgeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
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
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, facilityid, knowledgeid):
        try:
            facility = Facility.query.get_or_404(facilityid)
            knowledge = Knowledge.query.get_or_404(knowledgeid)
            facility.knowledge.remove(knowledge)
            db.session.commit()
            return None,200
        except:
          return'已经解除'









