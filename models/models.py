from sqlalchemy import Column, Integer, String, ForeignKey, Time
from db import Base

class User(Base):
    __tablename__ = "users"
    uid = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    username = Column(String, nullable=False)
    hashed_pwd = Column(String, nullable=False)
    created_at = Column(Time)


class Problems(Base):
    __tablename__ = "problems"
    pid = Column(Integer, primary_key=True)
    uid = Column(Integer, ForeignKey("users.uid"))
    title = Column(String)
    description = Column(String)
    attempted_approach = Column(String)
    type = Column(String)
    created_at = Column(Time)


class Hints(Base):
    __tablename__ = "hints"
    hid = Column(Integer, primary_key=True)
    pid = Column(Integer, ForeignKey("problems.pid"))
    hint_count = Column(Integer)
    content = Column(String)
    created_at = Column(Time)
