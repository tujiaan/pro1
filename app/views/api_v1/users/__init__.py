from flask import g, flash
from flask_restplus import Namespace, Resource

from app.ext import db
from app.models import User, Role
from app.utils.auth import user_require
from app.utils.auth.jwt import encode_jwt
from app.utils.tools.page_range import page_range
from app.views.api_v1.institutes import institute_model
from app.views.api_v1.roles import role_model

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

    @api.doc('')
    @api.route('/')
    class UsersFindView(Resource):
       @api.doc(params={'page':'页数','limit':'数量'})
       @api.marshal_with(user_model, as_list=True)
       @api.doc('查询所有用户信息')
       @api.marshal_with(user_model)
       @api.response(200, 'ok')
       @page_range()
       def get(self):
          list= User.query

          return list

       @api.doc('增加用户')
       @api.marshal_with(user_model)
       @api.expect(register_parser)
       @api.response(200, 'ok')
       def post(self):
           args=register_parser.parse_args()
           user=User(**args)
           db.session.add(user)
           db.session.commit()
           return user,200



@api.route('/<userid>')
class user(Resource):
     @api.doc('根据id查询用户信息')
     @api.marshal_with(user_model)
     @api.response(200, 'ok')

     def get(self,userid):
         user=User.query.filter_by(id=userid).first()
         return user

     @api.doc('根据id删除用户')
     @api.marshal_with(user_model)
     @api.response(200, 'ok')
     def delete(self,userid ):
         user = User.query.filter_by(id=userid).first()
         db.session.delete(user)
         db.session.commit()
         return None,200




@api.route('/<userid>/ins')
class UserHomeView(Resource):
    @api.doc('查询用户名下的机构')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(institute_model,as_list=True)
    @page_range()
    def get(self,userid):
        user=User.query.get_or_404(userid)
        return user.ins,200

@api.route('/<userid>/home')
class UserHomeView(Resource):
    @api.doc('查询用户名下的家庭')
    @api.marshal_with(home_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self,userid):
        user=User.query.get_or_404(userid)
        return user.home,200
@api.route('/<userid>/roles')
class UserRolesVsiew(Resource):
    @api.doc('查询用户的角色')
    @api.marshal_with(role_model,as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @ page_range()
    def get(self,userid):
        user=User.query.get_or_404(userid)
        return user.roles.all(),200


@api.route('/<userid>/roles/<roleid>')
class UserRoleView(Resource):
    @api.doc('给用户绑定角色')
    @api.response(200,'ok')
    def post(self,userid,roleid):
        try:
            user=User.query.get_or_404(userid)
            role=Role.query.get_or_404(roleid)


            user.roles.append(role)
            db.session.commit()
            return None,200
        except:return '该条记录已存在',400

    @api.doc('给用户解除角色')
    @api.response(200, 'ok')
    def delete(self, userid, roleid):
        try:
                user = User.query.get_or_404(userid)
                role = Role.query.get_or_404(roleid)
                user.roles.remove(role)
                db.session.commit()
                return None,200
        except:return '用户已不具备该角色',200




