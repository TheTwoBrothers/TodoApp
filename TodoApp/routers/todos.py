from fastapi import APIRouter,Depends,HTTPException,status,Path
from ..models import Todos
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel,Field
from starlette import status

from .auth import get_current_user
router=APIRouter()



def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close() 

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]


class TodosRequest(BaseModel):
    title: str =Field(min_length=3)
    description: str=Field(min_length=3,max_length=100)
    priority: int=Field(gt=0,lt=6)
    complete: bool


@router.get("/",status_code=status.HTTP_200_OK)
def real_all(user:user_dependency,db:db_dependency):
    if user is None:
            raise HTTPException(status_code=401,details='Authentication failed.')
    return db.query(Todos).filter(Todos.owner_id==user.get('user_id')).all() 

@router.get("/todos/{todo_id}",status_code=status.HTTP_200_OK)
def read_todo(user: user_dependency,db: db_dependency ,todo_id :int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401,details='Authentication failed.')
   
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id==user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404,detail='Todo not found.')

@router.post("/todos",status_code=status.HTTP_201_CREATED)
def create_todos(user:user_dependency,db:db_dependency,
                 todo_request:TodosRequest):

    if user is None:
         raise HTTPException(status_code=401,details='Authentication failed.')
    todo_model=Todos(**todo_request.model_dump(),owner_id=user.get('user_id'))

    db.add(todo_model)
    db.commit()



@router.put("/todos/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def update_todos(user:user_dependency,db:db_dependency,todo_request:TodosRequest,todo_id:int=Path(gt=0)):

    if user is None:
        raise HTTPException(status_code=401,details='Authentication failed.')
    
    todo_model=db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id==user.get('user_id')).first()

    if todo_model is  None:
        raise HTTPException(status_code=404,details='todo not found.')
    
    todo_model.title=todo_request.title
    todo_model.description=todo_request.description
    todo_model.priority=todo_request.priority
    todo_model.complete=todo_request.complete

    db.add(todo_model)
    db.commit()
@router.delete("/todos/{todo_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user:user_dependency,db:db_dependency,todo_id:int):

    if user is None:
            raise HTTPException(status_code=401,details='Authentication failed.')
     
    todo_model=db.query(Todos).filter(todo_id==Todos.id).filter(Todos.owner_id==user.get('user_id')).first()


    if todo_model is None:
        raise HTTPException(status_code=404,detail='todo not found.')

    db.query(Todos).filter(Todos.id==todo_id).filter(Todos.owner_id==user.get('user_id')).delete()
    db.commit()


