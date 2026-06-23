from sqlalchemy import Column, String, BigInteger, DateTime, ForeignKey, Enum, Boolean, Integer, Float, Date
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    STAGER = "stager"
    EMPLOYEE = "employee"
    MENTOR = "mentor"
    BRANCH_MANAGER = "branch_manager"
    HR = "hr"
    ADMIN = "admin"
    DIRECTOR = "director"

class CertificateLevel(enum.Enum):
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True) # Telegram ID
    username = Column(String, nullable=True)
    full_name = Column(String)
    phone = Column(String)
    birth_date = Column(Date, nullable=True)
    branch = Column(String)
    department = Column(String)
    position = Column(String)
    hire_date = Column(Date, default=datetime.utcnow)
    manager_name = Column(String, nullable=True)
    mentor_name = Column(String, nullable=True)
    role = Column(Enum(UserRole), default=UserRole.STAGER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    test_results = relationship("TestResult", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")
    progress = relationship("CourseProgress", back_populates="user")

class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    category = Column(String) # Umumiy, Sotuv, Kassa, Ombor, Undiruv, Liderlik
    is_active = Column(Boolean, default=True)

    lessons = relationship("Lesson", back_populates="course")
    tests = relationship("Test", back_populates="course")

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    content_type = Column(String) # Video, PDF, Text, etc.
    content_url = Column(String)
    order = Column(Integer)

    course = relationship("Course", back_populates="lessons")

class Test(Base):
    __tablename__ = "tests"
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String)
    min_score = Column(Integer, default=80) # 80%+ o'tdi

    course = relationship("Course", back_populates="tests")
    questions = relationship("Question", back_populates="test")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey("tests.id"))
    text = Column(String)
    options = Column(String) # JSON string: ["A", "B", "C"]
    correct_option = Column(String)

    test = relationship("Test", back_populates="questions")

class TestResult(Base):
    __tablename__ = "test_results"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    test_id = Column(Integer, ForeignKey("tests.id"))
    score = Column(Integer)
    is_passed = Column(Boolean)
    finished_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="test_results")

class Certificate(Base):
    __tablename__ = "certificates"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    level = Column(Enum(CertificateLevel)) # Bronze, Silver, Gold
    issued_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certificates")

class CourseProgress(Base):
    __tablename__ = "course_progress"
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    completed_lessons = Column(Integer, default=0)
    is_finished = Column(Boolean, default=False)

    user = relationship("User", back_populates="progress")
