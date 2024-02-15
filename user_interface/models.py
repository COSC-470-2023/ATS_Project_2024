from flask_login import UserMixin
from . import db
import sys
sys.path.insert(0, './database/processing')
import credentials as cred

db.Model.metadata.reflect(db.engine)

class Users(db.Model, UserMixin):
    __table__ = db.Model.metadata.tables['authorized_users']

    def __repr__(self):
        return self.DISTRICT