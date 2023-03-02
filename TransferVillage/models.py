from flask import current_app
from TransferVillage import db, login_manager
from datetime import datetime
import pytz
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

tz = pytz.timezone("Asia/Calcutta")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(str(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.String(125), primary_key=True)
    fname = db.Column(db.String(128))
    lname = db.Column(db.String(128))
    email = db.Column(db.String(140), unique=True, nullable=False)
    mobile_number = db.Column(db.String(11), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))
    modified_at = db.Column(db.DateTime, default=datetime.now(tz))
    files = db.relationship('File', backref='user', lazy='dynamic', uselist=True)

    def get_reset_token(self, expires_sec=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.fname}' '{self.lname}')"

    def __str__(self):
        return f"User('{self.fname}' '{self.lname}')"

class File(db.Model):
    id = db.Column(db.String(125), primary_key=True)
    folder_name = db.Column(db.String(125))
    original_filename = db.Column(db.String(125))
    filename = db.Column(db.String(125), unique=True)
    is_private = db.Column(db.Boolean, default=False)
    password = db.Column(db.String(1000))
    is_expiry = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    uploaded_at = db.Column(db.DateTime)
    link = db.Column(db.String(1000), nullable=False, unique=True)
    user_id = db.Column(db.String(125), db.ForeignKey('user.id'))

class Newsletter(db.Model):
    id = db.Column(db.String(125), primary_key=True)
    email = db.Column(db.String(140), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(tz))
