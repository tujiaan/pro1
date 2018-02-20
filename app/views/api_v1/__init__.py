import flask_restplus

from app.views import api_v1_bp as api_bp
from .users import api as user_ns
from .tools import api as tool_ns
api = flask_restplus.Api(api_bp,
                         title="消防API",
                         description="API",
                         contact="Tianjin Huitong Technology Co., Ltd",
                         contact_email="support@huitong-tech.com",
                         version="1.0", )

api.add_namespace(user_ns,path='/users')
api.add_namespace(tool_ns,path='/tools')

@api_bp.before_request
def before_request():
    pass