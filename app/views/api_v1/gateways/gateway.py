from flask_restplus import Resource

from . import api


class GatwayView(Resource):
    @api.doc('列出用户')
    def get(self):
        pass

    @api.doc('注册用户')
    def post(self):
        pass
