from flask_restplus.reqparse import RequestParser

sensor_parser = RequestParser()
sensor_parser.add_argument('gateway_id', type=str, help='网关id', required=True, location='form')
sensor_parser.add_argument('sensor_type', type=str, help='传感器类型', required=True, location='form')
sensor_parser.add_argument('sensor_place', type=str, help='传感器位置', required=True, location='form')

sensor_parser1 = RequestParser()
sensor_parser1.add_argument('gateway_id', type=str, help='网关id', required=False, location='form')
sensor_parser1.add_argument('sensor_type', type=str, help='传感器类型', required=False, location='form')
sensor_parser1.add_argument('sensor_place', type=str, help='传感器位置', required=False, location='form')

