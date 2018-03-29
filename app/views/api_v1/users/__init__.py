from flask import g, flash, request
from flask_restplus import Namespace, Resource
from sqlalchemy import select, text, and_, Boolean
from app.ext import db
from app.models import User, Role, Ins, Home, HomeUser, UserRole
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.auth.jwt import encode_jwt
from app.utils.tools.page_range import page_range, page_format
from app.views.api_v1.institutes import institute_model

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
        u1 = User.query.filter(User.contract_tel == args.get('contract_tel')).first()
        if u1 is not None:
            return None, 409
        u2 = User.query.filter(User.email == args.get('email')).first()
        if u2 is not None:
            return None, 409
        else:
            u = User(**args)
            db.session.add(u)
            db.session.commit()
            user_role1 = UserRole(user_id=u.id, role_id=1, if_usable=True)
            user_role2 = UserRole(user_id=u.id, role_id=2, if_usable=False)
            user_role3 = UserRole(user_id=u.id, role_id=3, if_usable=False)
            user_role4 = UserRole(user_id=u.id, role_id=4, if_usable=False)
            user_role5 = UserRole(user_id=u.id, role_id=5, if_usable=False)
            user_role7 = UserRole(user_id=u.id, role_id=7, if_usable=False)
            db.session.add_all([user_role1, user_role2, user_role3, user_role4, user_role5, user_role7])
            db.session.commit()
            return {'id': u.id}, 201


@api.route('/login/')
class LoginView(Resource):
    @api.doc('登陆')
    @api.expect(login_parser, validate=True)
    @api.response(201, '登录成功')
    @api.response(409, '用户不存在')
    def post(self):
        args = login_parser.parse_args()
        u = User.query.filter(and_(User.username == args.get('username'), User.password == args.get('password'),User.disabled == False)).first()
        user_role = UserRole.query.filter(UserRole.user_id == u.id).filter(UserRole.if_usable == True).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        if u is not None and args.get('roleid', None) in [i.id for i in roles]:
            jwt = encode_jwt(user_id=u.id)
            return {'jwt': jwt}, 200
        return None, 409
@api.route('/login1/')
class LoginView(Resource):
    @api.doc('登陆')
    @api.expect(login_parser1, validate=True)
    @api.response(201, '登录成功')
    @api.response(409, '用户不存在')
    def post(self):
        args = login_parser1.parse_args()
        u = User.query.filter(and_(User.username == args.get('username'), User.password == args.get('password'),User.disabled == False)).first()
        if u is not None:
            jwt = encode_jwt(user_id=u.id)
            return {'jwt': jwt}, 200
        else:return None, 409

@api.route('/roles/')
class RolesView(Resource):
    @user_require
    @api.header('jwt', 'JSON Web Token')
    @page_format(code=0, msg='200')
    @api.doc('获取权限')
    @api.marshal_with(role_model, as_list=True)
    @api.response(200, 'ok')
    @page_range()
    def get(self):
        u = g.user
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).filter(UserRole.if_usable == True).all()
        u.roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role))
        return u.roles, 200


@api.route('/homes/')
class UserHomeView1(Resource):
    @user_require
    @page_format(code='0', msg='success')
    @api.doc('查询自己关联的家庭')
    @api.header('jwt', 'JSON Web Token')
    @api.marshal_with(home_model, as_list=True)
    @page_range()
    def get(self):
        homeuser = HomeUser.query.filter(HomeUser.user_id == g.user.id).filter(HomeUser.if_confirm == True)
        list = Home.query.filter(Home.id.in_(i.home_id for i in homeuser))
        return list, 200


@api.route('/ins/')
class UserHomeView1(Resource):
    @user_require
    @page_format(code='0', msg='success')
    @api.header('jwt', 'JSON Web Token')
    @api.doc('查询自己关联的机构')
    @api.marshal_with(institute_model, as_list=True)
    @page_range()
    def get(self):
        ins = Ins.query.filter(Ins.user.contains(g.user))
        return ins, 200


@api.route('/password/')
class PasswordView(Resource):
    @api.doc('修改密码')
    @api.header('jwt', 'JSON Web Token')
    @api.expect(password_parser)
    @api.response(200, 'ok')
    @user_require
    def post(self):
        u = g.user
        args = password_parser.parse_args()
        if u.password == args.get('old_password'):
            u.password = args.get('password')
            db.session.commit()
            return None, 200
        else:
            return '权限不足', 204


@api.route('/profile/')
class ProfileView(Resource):
    @api.doc('获取用户个人信息')
    @api.marshal_with(user_model)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    def get(self):
        return g.user
@api.route('/<userid>/profile')
class UserProfile(Resource):
    @api.doc('修改用户个人信息')
    @api.response(200, 'ok')
    @api.expect(user_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin','superadmin'])
    def put(self,userid):
        user=User.query.get_or_404(userid)
        args=user_parser.parse_args()
        user_role=UserRole.query.filter(UserRole.user_id==g.user.id).all()
        roles=Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()

        def use(x):
            if int(x) == 0:
                return False
            else:
                return True
        if 'admin'in [i.name for i in roles] and 'superadmin'not in [i.name for i in roles]:
            if g.user.id==userid:
                if args['username']:
                    user.username=args['username']
                else:pass
                if args['password']:
                    user.password=args['password']
                else:pass
                if args['email']:
                    user.email=args['email']
                else:pass
                db.session.commit()
                return '修改成功',200
            else:return '权限不足',201
        else:
            if args['username']:
                user.username = args['username']
            else:
                pass
            if args['password']:
                user.password = args['password']
            else:
                pass
            if args['email']:
                user.email = args['email']
            else:
                pass
            if args['disabled']:
                user.disabled=use(args['disabled'])
            else:pass
            db.session.commit()
            return '修改成功', 200

@api.route('/<userid>/password')
class UserPassword(Resource):
    @api.doc('修改用户个人信息')
    @api.response(200, 'ok')
    @api.expect(userpassword_parser)
    @api.header('jwt', 'JSON Web Token')
    @role_require( ['superadmin'])
    def put(self,userid):
        user=User.query.get_or_404(userid)
        args=userpassword_parser.parse_args()
        user.password=args['password']
        db.session.commit()
        return '修改成功',200







@api.route('/telephone/')
class ProfileView(Resource):
    @api.doc('修改用户电话')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    @api.expect(telephone_parser)
    def post(self):
        u = g.user
        args = telephone_parser.parse_args()
        if u.contract_tel == args.get('old_contract_tel'):
            u.contract_tel = args.get('contract_tel')
            db.session.commit()
            return None, 200
        else:
            return '号码不正确', 201


@api.route('/email/')
class ProfileView(Resource):
    @api.doc('修改用户邮箱')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    @api.expect(email_parser)
    @api.response(200, 'ok')
    def post(self):
        u = g.user
        args = email_parser.parse_args()
        if u.email == args.get('old_email'):
            u.email = args.get('email')
            db.session.commit()
        return None, 204


@api.route('/username/')
class ProfileView(Resource):

    @api.doc('修改用户名')
    @api.header('jwt', 'JSON Web Token')
    @user_require
    @api.expect(username_parser)
    @api.response(200, 'ok')
    def post(self):
        u = g.user
        args = username_parser.parse_args()
        if u.username == args.get('old_username'):
            u.username = args.get('username')
            db.session.commit()
        return None, 204


@api.route('/')
class UserFindView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0,msg='ok')
    @api.response(200, 'ok')
    @api.marshal_with(user_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self):
        list = User.query
        return list,200
        # page = request.args.get('page',1)
        # limit = request.args.get('limit',10)
        #
        # query=db.session.query(User, Role).join(Role,User.roles).order_by(User.id)
        # total = query.count()
        #
        # query = query.offset((int(page) - 1) * limit).limit(limit)
        # # [{''} for i in query.all()]
        # _=[]
        # for i in query.all():
        #     __={}
        #     __['user_id']=i[0].id
        #     __['contract_tel']=i[0].contract_tel
        #     __['user_name']=i[0].username
        #     __['user_email'] = i[0].email
        #     __['role_id'] = i[1].id
        #     __['role_name'] = i[1].name
        #     __['role_disable'] = i[1].disabled
        #     _.append(__)
        # result = {
        #     'code': 200,
        #     'msg': 'ok',
        #     'count': total,
        #     'data': _
        # }
        # return result


@api.route('/<userid>')
class user(Resource):
    @api.doc('根据id查询用户信息')
    @api.marshal_with(user_model)
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def get(self, userid):
        user = User.query.get_or_404(userid)
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role))
        if 'superadmin' in [i.name for i in roles] or 'admin' not in [i.name for i in roles]:
            return user, 200
        else:
            return '权限不足', 200

    @api.header('jwt', 'JSON Web Token')
    @api.doc('根据id删除用户')
    @api.response(200, 'ok')
    @role_require(['admin', 'superadmin'])
    def delete(self, userid):
        user = User.query.get_or_404(userid)

        user.disabled = True
        role1 = g.user.roles.all()
        role2 = user.roles.all()
        if 'superadmin' in [i.name for i in role1]:
            db.session.commit()
            return None, 200
        elif 'admin' in [i.name for i in role1]:
            if 'admin' not in [i.name for i in role2] and 'superadmin' not in [i.name for i in role2]:
                db.session.commit()
                return None, 200
            else:
                return '权限不足', 201
        else:
            return '权限不足', 201


@api.route('/<userid>/ins')
class UserHomeView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询用户关联的机构')
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @api.marshal_with(institute_model, as_list=True)
    @page_range()
    def get(self, userid):
        user = User.query.get_or_404(userid)

        return user.ins, 200


@api.route('/<userid>/home')
class UserHomeView(Resource):

    @role_require(['admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.header('jwt', 'JSON Web Token')
    @api.doc('查询用户关联的家庭')
    @api.marshal_with(home_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self, userid):
        homeuser = HomeUser.query.get_or_404(userid)
        home = Home.query.filter(str(Home.id) in (homeuser.home_id))

        return home, 200


@api.route('/<userid>/auth')
class UserRolesVsiew(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @page_format(code=0, msg='ok')
    @api.doc('查询用户的角色')
    @api.marshal_with(role_model, as_list=True)
    @api.doc(params={'page': '页数', 'limit': '数量'})
    @page_range()
    def get(self, userid):
        user = User.query.get_or_404(userid)
        user_role1=UserRole.query.filter(UserRole.user_id ==g.user.id).all()
        user_role=UserRole.query.filter(UserRole.user_id==user.id).all()
        roles=Role.query.filter(Role.id.in_(i.role_id for i in user_role1))
        roles1= Role.query.filter(Role.id.in_(i.role_id for i in user_role))
        if 'admin' in [i.name for i in (roles1.all()) ] and 'superadmin' in [i.name for i in (roles.all())]:
            print(roles1.all()[1].if_usable)
            return roles1, 200
        else: return roles1, 200


    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    @api.doc('授权')
    @api.expect(role_parser)
    @api.response(200,'ok')
    def post(self,userid):
        user=User.query.get_or_404(userid)
        args=role_parser.parse_args()
        user_role = UserRole.query.filter(UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        user_role2=UserRole.query.filter(UserRole.user_id).filter(UserRole.role_id==2).first()
        user_role3= UserRole.query.filter(UserRole.user_id).filter(UserRole.role_id == 3).first()
        user_role4 = UserRole.query.filter(UserRole.user_id).filter(UserRole.role_id == 4).first()
        user_role5 = UserRole.query.filter(UserRole.user_id).filter(UserRole.role_id == 5).first()
        user_role7 = UserRole.query.filter(UserRole.user_id).filter(UserRole.role_id == 7).first()
        def use(x):
            if int(x)==0:
                return False
            else:return True
        if args['propertyuser']:
                print(args['propertyuser'])
                user_role2.if_usable=use(args['propertyuser'])
                print(user_role2.if_usable)
        else:pass
        if args['stationuser']:
                user_role3.if_usable=use(args['stationuser'])
        else:pass
        if args['119user']:
              user_role4.if_usable=use(args['119user'])
        else:pass
        if 'superadmin' in [i.name for i in roles]:
            if args['admin']:
                user_role5.if_usable=use(args['admin'])
            else:pass
        else:pass
        if args['knowledgeadmin']:
            user_role7.if_usable=use(args['knowledgeadmin'])
        else:pass
        db.session.commit()
        return '授权成功',200

@api.route('/<userid>/roles/<roleid>')
class UserRoleView(Resource):
    @api.doc('给用户绑定角色/增加xx用户')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def post(self, userid, roleid):
        role = Role.query.get_or_404(roleid)
        user_role = UserRole.query.filter( UserRole.user_id == g.user.id).all()
        user_role1=UserRole.query.filter(and_(UserRole.user_id==userid,UserRole.role_id==roleid)).first()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        if role.name != 'superadmin':
            if role.name not in ['admin', 'superadmin'] or 'superadmin' in [i.name for i in roles]:
                try:
                    user_role1.if_usable = True
                    db.session.commit()
                    return None, 200
                except:
                    return '该条记录已存在', 400
            elif role.name == 'admin'  and 'superadmin' in [i.name for i in roles]:
                try:
                    user_role1.if_usable = True
                    db.session.commit()
                    return None, 200
                except:
                    return '该条记录已存在', 400
            else:
                return '权限不足', 301
        else:
            pass

    @api.doc('给用户解除角色/删除xx用户')
    @api.response(200, 'ok')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin'])
    def delete(self, userid, roleid):
        role = Role.query.get_or_404(roleid)
        user_role1 = UserRole.query.filter(and_(UserRole.role_id == roleid), UserRole.user_id == userid).first()
        user_role = UserRole.query.filter( UserRole.user_id == g.user.id).all()
        roles = Role.query.filter(Role.id.in_(i.role_id for i in user_role)).all()
        if role.name not in ['admin', 'superadmin'] or 'superadmin' in [i.name for i in roles]:
            try:
                user_role1.if_usable = False
                db.session.commit()
                return None, 200
            except:
                return '用户已不具备该角色', 200
        elif role.name == 'admin' and 'superadmin' in [i.name for i in roles]:
            try:
                user_role1.if_usable = False
                db.session.commit()
                return None, 200
            except:
                return '用户已不具备该角色', 200
        else:
            return '权限不足', 301
