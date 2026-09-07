from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)       # "admin" หรือ "supervisor"
    dept = Column(String, nullable=True)         # เฉพาะ supervisor


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    dept = Column(String, nullable=False)
    hat_color = Column(String, nullable=False)


class BreakSession(Base):
    __tablename__ = "break_sessions"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    total_minutes = Column(Float, nullable=True)
