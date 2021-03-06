#!/usr/bin/python3
# coding: utf-8
from flask import Flask

from werkzeug.contrib.fixers import ProxyFix


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_pyfile('config.py')
    with app.app_context():
        from app.ext import ext_init
        from app.views import api_v1_bp
        ext_init(app)
        app.register_blueprint(api_v1_bp)
    return app
