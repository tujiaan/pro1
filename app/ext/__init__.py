from .cache import cache
from .csrf import csrf
from .db import db
from .logger import logger


def ext_init(app):
    db.init_app(app)
    cache.init_app(app)
    csrf.init_app(app)
    logger.init_app(app)
