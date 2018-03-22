
from .cache import cache
from .csrf import csrf
from .db import db
from .logger import logger
from .cors import cors



def ext_init(app):
    db.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    logger.init_app(app)
    cors.init_app(app)




