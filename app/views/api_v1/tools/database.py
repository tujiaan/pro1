from flask_restplus import Resource

from app.ext import db
from app.models import User,Menu
from app.views.api_v1.homeuser import HomeUserView1
from . import api


class InitDatabase(Resource):
    @api.doc('初始化数据库')
    def put(self):
        try:
            db.drop_all()
        except:
            pass
        db.create_all()
        return 'a'
class Utills(Resource):
    def post1(homeid):
        return HomeUserView1.post(homeid)
