from app.ext import  Jpush
import jpush


class JPush2(object):
    def post(self,alert):
        push = Jpush.create_push()
        push.audience = jpush.all_
        push.platform = jpush.all_
       # ios = jpush.ios(alert="Hello, IOS JPush!", sound="a.caf", extras={'k1': 'v1'})
        android = jpush.android(alert=alert, priority=1, style=1, alert_type=1,
                                big_text='jjjjjjjjjj',
                                extras={'k1': 'v1'})
        push.notification = jpush.notification(alert="Hello, JPush!", android=android)
        try:
            response = push.send()
        except Exception as e:
            print(e)