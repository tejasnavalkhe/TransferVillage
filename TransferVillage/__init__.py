from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from TransferVillage.config import Config
from flask_bcrypt import Bcrypt
from flask_mail import Mail


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()
login_manager.login_view = 'main.login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Please login to share the files.'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from TransferVillage.main.views import main
    from TransferVillage.errors.views import errors
    from TransferVillage.files.views import files
    app.register_blueprint(main)
    app.register_blueprint(errors)
    app.register_blueprint(files)

    return app
