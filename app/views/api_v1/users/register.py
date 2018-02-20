from flask import request
from flask_restplus import Resource

from app.ext import db
from app.models import User,Menu
from . import api


user_parser = api.parser()
user_parser.add_argument('username',
                           type=str,
                           help='用户名',
                           required=True,
                           location='form')

class Register(Resource):
    @api.doc('列出用户')
    def get(self):
        u=User.query.first()
        return {'username':u.username,'id':u.id}

    @api.doc('注册用户')
    @api.expect(user_parser)
    def post(self):
        username=request.form.get('username',None)
        if username is None:
            return None,401
        u=User(username=username)
        u.real_name= '测试用户'
        db.session.add(u)
        db.session.commit()
        return {'username':u.username,'id':u.id},201
