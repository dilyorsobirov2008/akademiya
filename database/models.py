from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum, Float, Boolean, DateTime, Text
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
    
    id = Column(Integer, primary_key=True)  # Telegram ID
    full_name = Column(String(255))
    phone = Column(String(20))
    dob = Column(Date)
    branch = Column(String(100))
    department = Column(String(100))
    position = Column(String(100))
    hire_date = Column(Date)
    manager_name = Column(String(255))
    mentor_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.TRAINEE)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    results = relationship("TestResult", back_populates="user")
    certificates = relationship("Certificate", back_populates="user")

class Course(Base):
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    description = Column(Text)
    category = Column(String(100)) # e.g., Onboarding, Sales, etc.
    
    lessons = relationship("Lesson", back_populates="course")
    tests = relationship("Test", back_populates="course")

class Lesson(Base):
    __tablename__ = 'lessons'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(255))
    content_type = Column(String(50)) # video, pdf, audio, text
    content_url = Column(String(500)) # or telegram file_id
    order = Column(Integer)
    
    course = relationship("Course", back_populates="lessons")

class Test(Base):
    __tablename__ = 'tests'
    
    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(255))
    min_score = Column(Integer, default=80)
    
    course = relationship("Course", back_populates="tests")
    questions = relationship("Question", back_populates="test")

class Question(Base):
    __tablename__ = 'questions'
    
    id = Column(Integer, primary_key=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    text = Column(Text)
    type = Column(String(50)) # single, multi, case
    options = Column(Text) # JSON or string delimited options
    correct_answer = Column(String(255))
    
    test = relationship("Test", back_populates="questions")

class TestResult(Base):
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    score = Column(Float)
    status = Column(String(50)) # Passed, Retake, Re-study
    completed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="results")

class Certificate(Base):
    __tablename__ = 'certificates'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    level = Column(String(50)) # Gold, Silver, Bronze
    issued_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="certificates")
