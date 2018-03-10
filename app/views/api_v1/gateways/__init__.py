from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import Gateway

api = Namespace('Gateway', description='网关相关接口')
from .model import *
@api.route('/<gatewayid>')
class GatewayView(Resource):
    @api.doc('查询特定的网关')
    @api.expect(gateway_model)
    @api.response(200,'ok')
    def get(self):############################
        return

