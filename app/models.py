from app import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)  # New field for profile name
    password = db.Column(db.String(60), nullable=False)

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)



class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(512), nullable=False)
    attribution = db.Column(db.String(100), nullable=False)  # New field for attribution
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    user = db.relationship('User', backref='quotes')  # Relationship to fetch username
