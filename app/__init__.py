from flask import Flask
from .config import Config
from .database import db
from .modules.routes import reports

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Register the blueprint
    app.register_blueprint(reports, url_prefix='/reports')

    return app

