from sqlalchemy import Column, Integer, String, Sequence, DateTime, ForeignKey
from flask_login import UserMixin, LoginManager, login_user
from sqlalchemy.orm import relationship
from database import connector
from time import gmtime, strftime


class User(UserMixin, connector.Manager.Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    fullname = Column(String(50))
    password = Column(String(12))
    username = Column(String(12))

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Message(connector.Manager.Base):
    __tablename__ = 'messages'
    id = Column(Integer, Sequence('message_id_seq'), primary_key=True)
    content = Column(String(500))
    sent_on = Column(String(20), default=strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    user_from_id = Column(Integer, ForeignKey('users.id'))
    user_to_id = Column(Integer, ForeignKey('users.id'))
    user_from = relationship("User", foreign_keys=[user_from_id])
    user_to = relationship("User", foreign_keys=[user_to_id])
