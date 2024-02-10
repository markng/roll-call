from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, BigInteger, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class CheckIn(Base):
    __tablename__ = 'check_ins'

    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger)
    user_name = Column(String)
    message_id = Column(BigInteger)
    channel_id = Column(BigInteger)
    guild_id = Column(BigInteger)
    at = Column(DateTime(timezone=True), server_default=func.now())
