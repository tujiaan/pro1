import datetime

from flask import g, request
from flask_restplus import Namespace, Resource
from sqlalchemy import DateTime

from app.ext import db
from app.models import HomeUser, Home
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
        if 'admin' or 'superadmin' in [i.name for i in g.user.roles]:

            return list, 200
        else:
            return list.filter(
                g.user in [(Home.query.get_or_404(HomeUser.home_id)).user] and HomeUser.if_confirm == True), 200


@api.route('/<homeid>')
class HomeUserView1(Resource):
    @api.doc('申请加入家庭/')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    #@api.expect(homeuser_parser)
    @user_require
    @api.response(200, 'ok')
    def post( self,homeid):
        homeuser = HomeUser()

        if Home.query.filter(Home.id == homeid):
            homeuser.home_id = homeid
            homeuser.user_id = g.user.id
            db.session.add(homeuser)
            db.session.commit()
            return '申请成功', 200
        else:
            return '家庭不存在', 201



@api.route('/<home_id>,<user_id>')
class HomeUserView2(Resource):
    @api.doc('批准加入家庭')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    @api.expect(homeuser_parser1)
    @user_require
    @api.response(200, 'ok')
    def post(self, homeid, userid):
        home = Home.query.get_or_404(homeid)
        if g.user.id == home.admin_user_id:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid and HomeUser.user_id == userid)
            homeuser.if_confirm = True
            homeuser.confirm_time=datetime.datetime.now(),
            db.session.commit()
            return '绑定成功', 200
        else:
            return '权限不足', 201

    @api.doc('删除家庭成员')
    @api.header('jwt', 'JSON Web Token')
    @role_require(['homeuser'])
    #@api.expect(homeuser_parser1)
    @user_require
    @api.response(200, 'ok')
    def post(self, homeid, userid):
        home = Home.query.get_or_404(homeid)
        if g.user.id == home.admin_user_id:
            homeuser = HomeUser.query.filter(HomeUser.home_id == homeid and HomeUser.user_id == userid)
            db.session.delete(homeuser)
            db.session.commit()
            return '绑定成功', 200
        else:
            return '权限不足', 201

