from flask import g
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import User
from app.utils.auth import user_require
from app.utils.auth.jwt import encode_jwt
from .models import *
from .parsers import *

api = Namespace('User', description='用户相关接口')

print(api.model('UserModel', {}))


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
    @user_require
    def post(self):
        pass


@api.route('/profile/')
class ProfileView(Resource):
    @api.doc('获取用户信息')
    @api.response(200, 'ok')
    @api.marshal_with(user_model)
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def get(self):
        return g.user

    @api.doc('修改用户信息')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def post(self):
        pass
