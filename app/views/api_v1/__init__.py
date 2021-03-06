import flask_restplus

from app.views import api_v1_bp as api_bp
from app.views.api_v1.facilities import api as facility_ns
from .gateways import api as gateway_ns
from .homes import api as home_ns
from .institutes import api as institut_ns
from .sensors import api as sensor_ns
from .tools import api as tool_ns
from .users import api as user_ns
from.knowledges import api as knowledge_ns
from .sensoralarms import api as sensoralarm_ns
from .roles import api as role_ns
from .useralarms import api as useralarmrecord_ns
from .communities import api as community_ns

api = flask_restplus.Api(api_bp,
                         title="消防API",
                         description="API",
                         contact="Tianjin Huitong Technology Co., Ltd",
                         contact_email="support@huitong-tech.com",
                         version="1.0", )

api.add_namespace(user_ns,path='/users')
api.add_namespace(tool_ns,path='/tools')
api.add_namespace(gateway_ns, path='/gateways')
api.add_namespace(facility_ns, path='/facilities')
api.add_namespace(home_ns, path='/homes')
api.add_namespace(sensor_ns, path='/sensors')
api.add_namespace(institut_ns, path='/institutes')
api.add_namespace(knowledge_ns,path='/knowledges')
api.add_namespace(sensoralarm_ns,path='/sensoralarms')
api.add_namespace(role_ns,path='/roles')
api.add_namespace(useralarmrecord_ns,path='/useralarmrecords')
api.add_namespace(community_ns,path='/community')



@api_bp.before_request
def before_request():
    pass