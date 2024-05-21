import logging
import traceback

from flask import Flask, g, request
from flask_cors import CORS
from api.response import authenticate_require, server_error, method_not_allowed

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

    @app.errorhandler(405)
    def unsupported_method_error(error):
        return method_not_allowed(msg=str(error))

    @app.errorhandler(Exception)
    def api_server_error(error):
        logging.error(traceback.format_exc())
        return server_error(msg=str(error))

    from api.v2 import v2_blu
    app.register_blueprint(v2_blu)
    return app
