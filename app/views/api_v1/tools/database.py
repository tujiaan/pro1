from flask_restplus import Resource

from app.ext import db
from app.models import User,Menu
from . import api


class InitDatabase(Resource):
    @api.doc('初始化数据库')
    def post(self,m_id):
        try:
            db.drop_all()
        except:
            pass
        db.create_all()
