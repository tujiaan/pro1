from flask_restplus import Namespace

api = Namespace('User', description='用户相关接口')

from .register import Register
api.add_resource(Register, '/register/')