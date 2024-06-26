"""
FastAPI quiz app entry point
"""

from fastapi import FastAPI,HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel,Session,select
from schema import Quiz, Points, get_session
from database import engine
from typing import Annotated


app = FastAPI()



# Allow any origin, credentials, and specific methods and headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development. Change this in production.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.on_event('startup')
def create_db_and_tables():
    """
    Creates the database and the quiz table if it doesn't exist
    """
    SQLModel.metadata.create_all(engine)


@app.get('/')
def get_quizes(session: Annotated[Session, Depends(get_session)]):
    """
    Returns all the quizes
    """
    quizes = session.exec(select(Quiz)).all()
    if quizes:
        return quizes
    return "No quizes in the database"


@app.post('/quiz/new')
def create_quiz_question(session:Annotated[Session, Depends(get_session)],question: str, option1: str,option2:str,option3:str,option4:str, correct_option: int):
    """
    Creates a new quiz question
    """
    options = [option1, option2, option3, option4]

    # Validate correct option
    if correct_option < 0 or correct_option > 3:
        raise ValueError("Correct option should be an index from 0 to 3")
    print("Here is the Question .. ->",question)
    new_quiz = Quiz(question=question, options=options, correct_option=correct_option)
    session.add(new_quiz)
    session.commit()
    session.refresh(new_quiz)
    return new_quiz


@app.post('/quiz/delete')
def delete_quiz_question(session: Annotated[Session, Depends(get_session)], id: int):
    """
    Deletes quiz by id
    """
    quiz = session.exec(select(Quiz).where(Quiz.id == id)).first()
    session.delete(quiz)
    session.commit()
    return quiz

@app.get('/{id}')
def get_quiz_question_by_id(session:Annotated[Session,Depends(get_session)],id:int):
    """
    Returns the quiz question by id
    """
    quiz = session.exec(select(Quiz).where(Quiz.id == id)).first()
    if quiz:
        return quiz
    raise HTTPException(status_code=404,detail=f"Question not found with id {id}")


@app.post('/points/add')
def add_points(session: Annotated[Session, Depends(get_session)]):
    """
    Adds a point to the credit points counter
    """
    points = session.exec(select(Points)).first()
    if points:
        points.points += 1
        session.commit()
        session.refresh(points)
        return points
    else:
        points = Points(points=1)
        session.add(points)
        session.commit()
        session.refresh(points)
        return points
    

@app.get('/points/total')
def get_points(session: Annotated[Session, Depends(get_session)]):
    """
    Returns the total points
    """
    points = session.exec(select(Points)).first()
    if points:
        print(points)
        return points
    raise HTTPException(status_code=404, detail="No points found")


@app.patch('/points/edit')
def edit_points(session: Annotated[Session, Depends(get_session)], points_update: Points):
    """
    Edit the points counter
    """
    points = session.exec(select(Points)).first()
    print(points)
    if points:
        points.points = points_update.points
        session.commit()
    raise HTTPException(status_code=404, detail='No points found')