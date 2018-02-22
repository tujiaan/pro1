from flask_restplus.reqparse import RequestParser

login_parser = RequestParser()
login_parser.add_argument('username', type=str, help='用户名', required=True, location='form')
login_parser.add_argument('password', type=str, help='密码', required=True, location='form')

register_parser = login_parser.copy()
register_parser.add_argument('contract_tel', type=str, help='电话号码', required=True, location='form')
register_parser.add_argument('email', type=str, help='邮箱', required=True, location='form')
