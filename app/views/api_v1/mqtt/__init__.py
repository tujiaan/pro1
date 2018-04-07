from flask import request
from flask_restplus import Namespace, Resource
from flask_restplus.reqparse import RequestParser
from app.ext import mqtt
api=Namespace('Mqtt',description='MQTT操作')
payload_parser=RequestParser()
payload_parser.add_argument('payload',help='社区名称',required=True,location='json')
@api.route('/')
class Command(Resource):
    @api.expect(payload_parser,validate=False)
    def post(self,theme):
        data=request.data
        mqtt.publish(str(theme),data)
        return None