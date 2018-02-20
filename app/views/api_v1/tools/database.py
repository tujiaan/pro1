from flask_restplus import Resource

from app.ext import db
from app.models import User,Menu
from . import api


class InitDatabase(Resource):
    @api.doc('初始化数据库')
    def put(self):
        print(db.get_tables_for_bind())
        a=db.drop_all()
        db.create_all()
        return 'a'
