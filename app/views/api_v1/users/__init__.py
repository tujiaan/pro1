from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import User
from app.utils.auth import user_require
from app.utils.auth.jwt import encode_jwt
from .parsers import *

api = Namespace('User', description='用户相关接口')
from .models import *

@api.route('/register/')
class RegisterView(Resource):
    @api.doc('注册用户')
    @api.expect(register_parser, validate=True)
    @api.response(201, '注册成功')
    @api.response(409, '用户重复')
    def post(self):
        args = register_parser.parse_args()
        u = User.query.filter_by(username=args.get('username')).first()
        if u is not None:
            return None, 409
        u = User(**args)
        db.session.add(u)
        db.session.commit()
        return {'id': u.id}, 201


@api.route('/login/')
class LoginView(Resource):
    @api.doc('登陆')
    @api.expect(login_parser, validate=True)
    @api.response(201, '注册成功')
    @api.response(409, '用户重复')
    def post(self):
        args = login_parser.parse_args()
        u = User.query.filter_by(username=args.get('username'), password=args.get('password')).first()
        if u is not None:
            jwt = encode_jwt(user_id=u.id)
            return {'jwt': jwt}, 200
        return None, 401


@api.route('/roles/')
class RolesView(Resource):
    @api.doc('获取权限')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def get(self):
        u = g.user
        print(u.roles)
        return None


@api.route('/password/')
class PasswordView(Resource):
    @api.doc('找回密码')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def get(self):
        u = g.user
        return u.password

    @api.doc('修改密码')
    @api.header('jwt', 'JSON Web Token')
    @api.expect(password_parser)
    @user_require
    def post(self):
        u = g.user
        args = password_parser.parse_args()
        if u.password == args.get('old_password'):
            u.password = args.get('password')
            db.session.commit()
        return None, 204


@api.route('/profile/')
class ProfileView(Resource):
    @api.doc('获取用户信息')
    @api.marshal_with(user_model)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def get(self):
        return g.user

    @api.doc('修改用户电话')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    @api.expect(telephone_parser)
    def post(self):
        u = g.user
        args = telephone_parser.parse_args()
        if u.contract_tel == args.get('old_contract_tel'):
            u.contract_tel= args.get('contract_tel')
            db.session.commit()
        return None, 204


    @api.doc('修改用户邮箱')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    @api.expect(email_parser)
    def post(self):
        u = g.user
        args = email_parser.parse_args()
        if u.email == args.get('old_email'):
            u.email= args.get('email')
            db.session.commit()
        return None, 204

    api.route('/  /')
    class usersFindView(Resource):
       @api.doc('查询所有用户信息')
       @api.marshal_with(user_model)
       @api.response(200, 'ok')
       def get(self):
          list= User.query.all()
          print(len(list))
          return


