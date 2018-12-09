from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from hashlib import md5
from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    firstname = db.Column(db.String(64), index=True, unique=True)
    lastname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    groups = db.relationship("Group", backref="creator", lazy="dynamic")

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode("utf-8")).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    individuals = db.Column(db.String)
    indiv_display = db.Column(db.String)
    creation_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    config = db.relationship("GroupConfig", backref="group", lazy="dynamic")

    def __repr__(self):
        return "<Group {} - {}>".format(self.user_id, self.creation_time)


class GroupConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pairs = db.Column(db.String)
    separated = db.Column(db.String)
    max_size = db.Column(db.Integer)
    num_groups = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    group_id = db.Column(db.Integer, db.ForeignKey("group.id"))

    def __repr__(self):
        return "<GroupConfig {} - {}>".format(self.user_id, self.group_id)
