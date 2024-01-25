from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CheckIn(Base):
    __tablename__ = 'check_ins'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    user_name = Column(String)
    message_id = Column(Integer)
    channel_id = Column(Integer)
    guild_id = Column(Integer)
    at = Column(DateTime(timezone=True), default=datetime.now())
