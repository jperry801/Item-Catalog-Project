import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class ToyNames(Base):
    __tablename__ = 'toynames'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'name': self.name,
            'id': self.id,
        }


class Inventory(Base):
    __tablename__ = 'inventory'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    toynames_id = Column(Integer, ForeignKey('toynames.id'))
    toynames = relationship(ToyNames)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# We added this serialize function to be able to send JSON objects
# in a serializable format
    @property
    def serialize(self):

        return {
           'name': self.name,
           'description': self.description,
           'id': self.id,
        }

engine = create_engine('sqlite:///appwithusers.db')
Base.metadata.create_all(engine)
