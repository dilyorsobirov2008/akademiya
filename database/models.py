from sqlalchemy import Column, Integer, BigInteger, String, Date, ForeignKey, Enum, Float, Boolean, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    TRAINEE = "stajer"
    EMPLOYEE = "xodim"
    MENTOR = "mentor"
    BRANCH_MANAGER = "filial_rahbari"
    HR = "hr"
    ADMIN = "admin"
    DIRECTOR = "direktor"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True)  # Telegram ID (can be large)
    full_name = Column(String(255))
    phone = Column(String(20))
    dob = Column(Date, nullable=True)
    branch = Column(String(100))
    department = Column(String(100))
    position = Column(String(100))
    hire_date = Column(Date, nullable=True)
    manager_name = Column(String(255))
    mentor_name = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.TRAINEE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    results = relationship("TestResult", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")
    course_progress = relationship("CourseProgress", back_populates="user")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255))
    description = Column(Text, nullable=True)
    category = Column(String(100))  # onboarding, sotuv, kassir, ombor, undiruv, liderlik
    order_num = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.order_num")
    tests = relationship("Test", back_populates="course")

class Lesson(Base):
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(255))
    content_type = Column(String(50))  # video, pdf, audio, text, checklist
    content_url = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    order_num = Column(Integer, default=0)
    
    course = relationship("Course", back_populates="lessons")

class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(255))
    min_score = Column(Integer, default=80)
    
    course = relationship("Course", back_populates="tests")
    questions = relationship("Question", back_populates="test", order_by="Question.order_num")

class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    text = Column(Text)
    q_type = Column(String(50))  # single, multi, case
    options = Column(Text)  # JSON string: ["variant1", "variant2", ...]
    correct_answer = Column(String(500))  # For single: "A", for multi: "A,C"
    order_num = Column(Integer, default=0)
    
    test = relationship("Test", back_populates="questions")

class TestResult(Base):
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    score = Column(Float)
    status = Column(String(50))  # passed, retake, restudy
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="results")

class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    level = Column(String(50))  # gold, silver, bronze
    issued_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="certificates")

class CourseProgress(Base):
    __tablename__ = 'course_progress'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    completed_lessons = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="course_progress")

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
