from flask import request
from flask_restplus import Namespace, Resource
from flask_restplus.reqparse import RequestParser
from app.ext import mqtt
api=Namespace('Mqtt',description='MQTT操作')
payload_parser=RequestParser()
payload_parser.add_argument('payload',help='社区名称',required=True,location='json')
#payload_parser.add_argument('theme',)
@api.route('/<gatewayid>/')
class Command(Resource):
    @api.expect(payload_parser,validate=False)
    def post(self,gatewayid):
        data=request.data
        theme=str(gatewayid)+'/cmd'
        mqtt.publish(theme,data)
        return None