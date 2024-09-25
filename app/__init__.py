#__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO
from flask_cors import CORS

db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()
socketio = SocketIO()
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
    migrate.init_app(app, db)
    csrf.init_app(app)
    CORS(app, resources={r"/*": {"origins": "https://quoteboard.work"}})
    socketio.init_app(app, cors_allowed_origins="https://quoteboard.work")

    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
