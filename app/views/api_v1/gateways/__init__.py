from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Gateway

api = Namespace('Gateway', description='网关相关接口')
from .parser import *
@api.route('/')
class GatewayView(Resource):
    @api.doc('新增网关')
    @api.expect(gateway_parser)
    @api.response(200,'ok')
    def post(self):
        args=gateway_parser.parse_args()
        gateway=Gateway(**args)
        db.session.add(gateway)
        db.session.commit()
        return

