from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'main.login' 


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('secrets.cfg', silent=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
