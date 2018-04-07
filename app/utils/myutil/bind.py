from _sha256 import sha256
import time
from pprint import pprint
import requests

import app
from instance import config


class utils(object ):
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        config = app.config.copy()
        self.appkey = config.get('APP_KEY')
        self.mastersecret = config.get('MASTER_SECRET')
        self.appid = config.get('APP_ID')
    def getAuth( self):
        now=int(time.time() * 1000)
        sign = sha256(("FUvUQj6C2J69HKCGDKDrc2" + str(now) + '7MmIrGUUL16f8RF2OTwFE4').encode())
        url = 'https://restapi.getui.com/v1/1GIGIfZvFyA6iMf5kq3rV3/auth_sign'
        data = {
            "sign": sign.hexdigest(),
            "timestamp":str(now),
            "appkey": "FUvUQj6C2J69HKCGDKDrc2"
        }
        res = requests.post(url=url, json=data)
        result=(res.json()).get('auth_token')+str('$$$$$$')+(res.json()).get('expire_time')
        pprint(result)
        return result,200
    def bind(self,userid,cid):
        headers={
            'Content-Type':'application/json',
            'authtoken':self.getAuth(self)
        }
        url='https://restapi.getui.com/v1/1GIGIfZvFyA6iMf5kq3rV3/bind_alias'
        data={
            "alias_list": [{"cid": cid, "alias": userid}]
        }
        res = requests.post(url=url,headers=headers, json=data)
        result=res.json()




