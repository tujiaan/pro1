import jpush
from flask_restplus import Namespace, Resource

from app.ext import Jpush

api = Namespace('Test', description='测试接口')


@api.route('/jpush/')
class JPush(Resource):
    def post(self):
        push = Jpush.create_push()
        push.audience = jpush.all_
        push.notification = jpush.notification(alert="hello python jpush api")
        push.platform = jpush.all_
        try:
            response = push.send()
        except Exception as e:
            print(e)


@api.route('/jpush2/')
class JPush2(Resource):
    def post(self):
        push = Jpush.create_push()
        push.audience = jpush.all_
        push.platform = jpush.all_
        #ios = jpush.ios(alert="Hello, IOS JPush!", sound="a.caf", extras={'k1': 'v1'})
        android = jpush.android(alert="Hello, Android msg", priority=1, style=1, alert_type=1, big_text='jjjjjjjjjj',
                                extras={'k1': 'v1'})
        push.notification = jpush.notification(alert="Hello, JPush!", android=android)#,ios=ios)
        try:
            response = push.send()
        except Exception as e:
            print(e)
