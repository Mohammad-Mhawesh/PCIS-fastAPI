from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    phone_number = Column(String)


class Call(Base):
    __tablename__ = "calls"

    call_id = Column(Integer, primary_key=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))
    client_id = Column(Integer, ForeignKey(
        "clients.client_id", ondelete="CASCADE"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    created_by = Column(Integer, ForeignKey(
        "users.user_id", ondelete="CASCADE"), nullable=False)
    machine_id = Column(Integer,ForeignKey("machines.machine_id",ondelete="CASCADE"), nullable = False)
    cause = Column(String,nullable = False,server_default = 'Cause not recorded')
    closed = Column(Boolean, nullable = False, server_default = 'False')
    engineer_response = Column(String,server_default = "Waiting for engineer's response")
    client = relationship("Client", foreign_keys=[client_id])
    assigned_to_user = relationship("User", foreign_keys=[assigned_to_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    machine = relationship("Machine", foreign_keys = [machine_id])



class Client(Base):
    __tablename__ = "clients"

    client_id = Column(Integer, primary_key=True, nullable=False)
    client_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True),
                        nullable=False, server_default=text('now()'))


class Machine(Base):
    __tablename__ = "machines"

    machine_id = Column(Integer, primary_key=True, nullable=False, server_default= text('0'))
    client_id = Column(Integer, ForeignKey(
        "clients.client_id", ondelete="CASCADE"), nullable=False)
