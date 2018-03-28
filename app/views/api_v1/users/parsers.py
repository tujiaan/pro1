from flask_restplus.reqparse import RequestParser

login_parser = RequestParser()
login_parser.add_argument('roleid', type=str, help='角色id', required=True, location='form')
login_parser.add_argument('username', type=str, help='用户名', required=True, location='form')
login_parser.add_argument('password', type=str, help='密码', required=True, location='form')

login_parser1 = RequestParser()
login_parser1.add_argument('username', type=str, help='用户名', required=True, location='form')
login_parser1.add_argument('password', type=str, help='密码', required=True, location='form')


register_parser = RequestParser()
register_parser.add_argument('username', type=str, help='用户名', required=True, location='form')
register_parser.add_argument('password', type=str, help='密码', required=True, location='form')
register_parser.add_argument('contract_tel', type=str, help='电话号码', required=True, location='form')
register_parser.add_argument('email', type=str, help='邮箱', required=True, location='form')

password_parser = RequestParser()
password_parser.add_argument('old_password', type=str, help='原密码', required=True, location='form')
password_parser.add_argument('password', type=str, help='新密码', required=True, location='form')

telephone_parser = RequestParser()
telephone_parser.add_argument('old_contract_tel', type=str, help='原电话', required=True, location='form')
telephone_parser.add_argument('contract_tel', type=str, help='新电话', required=True, location='form')

email_parser = RequestParser()
email_parser.add_argument('old_email', type=str, help='原邮箱', required=True, location='form')
email_parser.add_argument('email', type=str, help='新邮箱', required=True, location='form')

username_parser=RequestParser()
username_parser.add_argument('old_username',type=str,help='原用户名',location='form')
username_parser.add_argument('username',type=str,help='新用户名',location='form')

