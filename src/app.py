"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


# Banco de dados
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, Activity, Student

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria as tabelas se não existirem
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")




@app.get("/activities")
def get_activities():
    session = SessionLocal()
    activities = session.query(Activity).all()
    result = {}
    for activity in activities:
        result[activity.name] = {
            "description": activity.description,
            "schedule": activity.schedule,
            "max_participants": activity.max_participants,
            "participants": [student.email for student in activity.participants]
        }
    session.close()
    return result


# NOVO: Estatísticas gerais das atividades

@app.get("/activities/statistics")
def get_activities_statistics():
    session = SessionLocal()
    activities = session.query(Activity).all()
    stats = {}
    for activity in activities:
        stats[activity.name] = {
            "max_participants": activity.max_participants,
            "current_participants": len(activity.participants),
            "vacancies": activity.max_participants - len(activity.participants),
        }
    session.close()
    return stats


# NOVO: Histórico de participação por atividade

@app.get("/activities/{activity_name}/history")
def get_activity_history(activity_name: str):
    session = SessionLocal()
    activity = session.query(Activity).filter_by(name=activity_name).first()
    if not activity:
        session.close()
        raise HTTPException(status_code=404, detail="Activity not found")
    result = {
        "activity": activity.name,
        "participants": [student.email for student in activity.participants],
        "max_participants": activity.max_participants,
        "vacancies": activity.max_participants - len(activity.participants),
        "description": activity.description,
        "schedule": activity.schedule
    }
    session.close()
    return result



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, name: str = None, grade_level: str = None):
    session = SessionLocal()
    activity = session.query(Activity).filter_by(name=activity_name).first()
    if not activity:
        session.close()
        raise HTTPException(status_code=404, detail="Activity not found")

    student = session.query(Student).filter_by(email=email).first()
    if not student:
        if not name or not grade_level:
            session.close()
            raise HTTPException(status_code=400, detail="Student not found. Provide name and grade_level to register.")
        student = Student(name=name, email=email, grade_level=grade_level)
        session.add(student)
        session.commit()
        session.refresh(student)

    if student in activity.participants:
        session.close()
        raise HTTPException(status_code=400, detail="Student is already signed up")

    activity.participants.append(student)
    session.commit()
    session.close()
    return {"message": f"Signed up {email} for {activity_name}"}



@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    session = SessionLocal()
    activity = session.query(Activity).filter_by(name=activity_name).first()
    if not activity:
        session.close()
        raise HTTPException(status_code=404, detail="Activity not found")

    student = session.query(Student).filter_by(email=email).first()
    if not student or student not in activity.participants:
        session.close()
        raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

    activity.participants.remove(student)
    session.commit()
    session.close()
    return {"message": f"Unregistered {email} from {activity_name}"}
