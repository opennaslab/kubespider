import logging

from flask import Flask, g, request
from flask_cors import CORS
from api.response import authenticate_require, server_error

from utils.global_config import APPConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(APPConfig)
    CORS(app)

    @app.before_request
    def get_auth():
        g.auth = False
        if not APPConfig.AUTH_TOKEN:
            g.auth = True
            return
        authorization = request.headers.get("Authorization", "")
        try:
            auth_type, auth_info = authorization.split(None, 1)
            auth_type = auth_type.lower()
            if auth_type == "bearer" and auth_info == APPConfig.AUTH_TOKEN:
                g.auth = True
        except Exception as err:
            logging.debug("Auth Failed: %s", err)

    @app.errorhandler(401)
    def unauthorized_error(error):
        return authenticate_require(msg=str(error))

    @app.errorhandler(500)
    def api_server_error(error):
        return server_error(msg=str(error))

    from api.v1 import v1_blu, health_blu
    from api.v2 import v2_blu
    app.register_blueprint(v1_blu)
    app.register_blueprint(health_blu)
    app.register_blueprint(v2_blu)
    return app
