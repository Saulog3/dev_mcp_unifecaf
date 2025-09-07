from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

activity_participant = Table(
    'activity_participant', Base.metadata,
    Column('activity_id', Integer, ForeignKey('activities.id')),
    Column('student_id', Integer, ForeignKey('students.id'))
)

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    participants = relationship('Student', secondary=activity_participant, back_populates='activities')

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    grade_level = Column(String)
    activities = relationship('Activity', secondary=activity_participant, back_populates='participants')
