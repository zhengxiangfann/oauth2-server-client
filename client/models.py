import time
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)


from authlib.integrations.flask_client import OAuth



db = SQLAlchemy()
# db.engine =  create_engine('mysql+pymysql://root:root@')
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    def __str__(self):
        return self.username
    def get_user_id(self):
        return self.id
    def check_password(self, password):
        return password == 'valid'


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()


def fetch_token(name):
    token = OAuth2Token.query.filter_by(name=name, user=current_user).first()
    return token.to_token()


def update_token(name, token, refresh_token=None, access_token=None):
    if refresh_token:
        item = OAuth2Token.filter_by(name=name, refresh_token=refresh_token).first()
    elif access_token:
        item = OAuth2Token.filter_by(name=name, access_token=access_token).first()
    else:
        return
    if not item:
        return
    # update old token
    item.access_token = token['access_token']
    item.refresh_token = token.get('refresh_token')
    item.expires_at = token['expires_at']
    db.session.commit()
