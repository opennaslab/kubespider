from flask import Flask, g, request
from core.api.response import authenticate_require, server_error
from core.middleware.download_provider.manager import DownloadManager
from core.middleware.source_provider.manager import SourceManager
from core.middleware.notification_provider.manager import NotificationManager
from core.statemachine.manager import StateMachineManager
from core.models import db
from utils.global_config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    DownloadManager(app)
    SourceManager(app)
    NotificationManager(app)
    StateMachineManager(app)

    @app.before_request
    def get_auth():
        if not Config.AUTH_TOKEN:
            g.auth = True
        else:
            if request.headers is None:
                g.auth = False
            else:
                authorization = request.headers.get("Authorization")
                if not authorization:
                    g.auth = False
                try:
                    auth_type, auth_info = authorization.split(None, 1)
                    auth_type = auth_type.lower()
                    if auth_type == "bearer" and auth_info == Config.AUTH_TOKEN:
                        g.auth = True
                    g.auth = False
                except ValueError:
                    g.auth = False

    @app.errorhandler(401)
    def unauthorized_error(error):
        return authenticate_require()

    @app.errorhandler(500)
    def api_server_error(error):
        return server_error()

    from core.api.v2 import v2_blu
    app.register_blueprint(v2_blu)
    return app
