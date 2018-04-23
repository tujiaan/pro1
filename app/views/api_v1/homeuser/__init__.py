import datetime

from flask import g, request
from flask_restplus import Namespace, Resource, abort
from sqlalchemy import DateTime, and_

from app.ext import db
from app.models import HomeUser, Home, UserRole, Role
from app.utils.auth import user_require
from app.utils.auth.auth import role_require
from app.utils.tools.page_range import page_format, page_range
from app.views.api_v1.homeuser.parser import  homeuser_parser1

api = Namespace('HomeUser', description='用户家庭相关接口')
from .models import *


@api.route('/')
class HomeUsersView(Resource):
    @api.header('jwt', 'JSON Web Token')
    @role_require(['admin', 'superadmin', 'homeuser'])
    @page_format(code=0, msg='ok')
    @api.doc('显示家庭用户列表')
    @api.marshal_with(homeuser_model)
    @user_require
    @api.response(200, 'ok')
    @page_range()
    def get(self):
        list = HomeUser.query
        home = Home.query.filter(Home.admin_user_id == g.user.id).filter(Home.disabled == False).all()
        if home:
            if g.role.name in ['admin', 'superadmin']:
                return list, 200
            else:
                return list.filter(HomeUser.home_id.in_(i.id for i in home)).filter(HomeUser.if_confirm == True),
        else: abort(404, message='家庭不存在')


@api.route('/<homeid>/')
class HomeUserView1(Resource):
    @api.doc('申请加入家庭')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.response(200, 'ok')
    def post(self, homeid):
        home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid)
            if Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first():
                if g.user.id not in [i.user_id for i in homeuser]:
                    homeuser = HomeUser()
                    homeuser.home_id = homeid
                    homeuser.user_id = g.user.id
                    db.session.add(homeuser)
                    db.session.commit()
                    return '申请成功', 200
                else:
                    return '您已经是该家庭成员', 201
        else:return '家庭不存在',401

    @page_format(code=0, msg='ok')
    @api.doc('显示家庭申请')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.marshal_with(homeuser_model, as_list=True)
    @api.response(200, 'ok')
    @page_range()
    def get(self, homeid):
       home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
       if home:
           if g.user.id == home.admin_user_id:
               homeuser = HomeUser.query.filter(HomeUser.if_confirm == False).filter(HomeUser.home_id == homeid)
               return homeuser, 200
           else: return '权限不足', 200
       else:abort(404, message='家庭不存在')


@api.route('/<homeid>/<userid>/')
class HomeUserView2(Resource):
    @api.header('jwt', 'JSON Web Token')
    @api.doc('批准加入家庭')
    @role_require(['homeuser'])
    @api.response(200, 'ok')
    @user_require
    def put(self, homeid, userid):
        home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
        if home:
            homeuser = HomeUser.query.filter(and_(HomeUser.home_id == homeid, HomeUser.user_id == userid)).first()
            homeuser.if_confirm = True
            homeuser.confirm_time = datetime.datetime.now()
            if g.user.id == home.admin_user_id:
                db.session.commit()
                return '绑定成功', 200
            else:
                return '权限不足', 201
        else: return '家庭不存在', 201

    @api.doc('删除家庭成员记录')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser', 'admin', 'superadmin'])
    @api.response(200, 'ok')
    def delete(self, homeid, userid):
        home = Home.query.filter(Home.disabled == False).filter(Home.id == homeid).first()
        if home:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid).filter(HomeUser.user_id == userid).first()
            db.session.delete(homeuser)
            if g.role.name == 'homeuser':
                if g.user.id == home.admin_user_id:
                    db.session.commit()
                    return '删除成功', 200
                else:
                    return '权限不足', 201
            else:
                db.session.commit()
                return'删除成功', 200
        else:return '家庭不存在', 201

