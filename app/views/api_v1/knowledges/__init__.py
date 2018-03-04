from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Knowledge
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.facilities import facility_model
from app.views.api_v1.knowledges.parser import knowledge_parser, knowledge_parser1

api = Namespace('Knowledges', description='知识相关接口')
from .models import *
@api.route('/')
class Knowledges(Resource):
    @page_format(code=200,msg='ok')
    @api.doc('查询知识列表')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(knowledges_model,as_list=True)
    @api.response(200,'ok')
    @page_range()
    def get(self):

            list=Knowledge.query
            return list,200

    @api.doc('添加知识')
    @api.expect(knowledge_parser)
    @api.response(200,'ok')
    def post(self):
        args=knowledge_parser.parse_args()
        knowledge=Knowledge(**args)
        db.session.add(knowledge)
        db.session.commit()
        return None,200

@api.route('/<knowledgeid>')
class KnowledgeView(Resource):
    @api.doc('根据id查询知识详情')
    @api.marshal_with(knowledges_model)
    @api.response(200,'ok')
    def get(self,knowledgeid):
        knowledge=Knowledge.query.get_or_404(knowledgeid)
        return knowledge,200
    @api.doc('根据id更新知识')
    @api.expect(knowledge_parser1)
    @api.response(200,'ok')
    def put(self,knowledgeid):
        args=knowledge_parser1.parse_args()
        knowledge=Knowledge.query.get_or_404(knowledgeid)
        if args['type']:
            knowledge.type=args.get('type')
        else:pass
        if args['content']:
            knowledge.content=args.get('content')
        else:pass
        if args['title']:
            knowledge.title=args.get('title')
        else:pass
        db.session.commit()
        return None,200
    @api.doc('根据id删除知识')
    @api.response(200,'ok')
    def delete(self,knowledgeid):
        knowledge = Knowledge.query.get_or_404(knowledgeid)
        db.session.delete(knowledge)
        db.session.commit()
        return None,200
@api.route('/<knowledgeid>/facility')
class KnowledgeFacilityView(Resource):
    @page_format(code='200', message='successs')
    @api.doc('根据知识查找对应的设施')
    @api.marshal_with(facility_model,as_list=True)
    @api.response(200,'ok')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,knowledgeid) :
        knowledge=Knowledge.query.get_or_404(knowledgeid)
        return knowledge.facility,200
