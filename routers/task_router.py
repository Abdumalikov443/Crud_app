from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi_jwt_auth import AuthJWT
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_

from models import Task, User
from db import db_dependency

task = APIRouter(
    prefix="/task",
    tags=["task"]
)

templates = Jinja2Templates(directory="templates")

# All Tasks
@task.get('/', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def list_all_tasks(db: db_dependency, 
                         request: Request,
                         Authorize: AuthJWT = Depends()):
    try:    
        Authorize.jwt_required()
    except Exception as e:
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    
    user = Authorize.get_jwt_subject()
    current_user = db.query(User).filter(
        or_(
            User.username == user,
            User.email == user
        )).first()

    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.is_staff:
        tasks = db.query(Task).all()
        return templates.TemplateResponse("task/task_list.html", {"request": request, "tasks": tasks})
    else:
        #get tasks only that user created
        tasks = db.query(Task).filter(Task.user_id == current_user.id).all()
        if tasks is None:
            return {"message": "You have not created any tasks yet."}
    return templates.TemplateResponse("task/task_list.html", {"request": request, "tasks": tasks})


# Create side
@task.get('/create', status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def create_task(request: Request):
    return templates.TemplateResponse('task/task_create.html', {"request": request})

@task.post('/create', status_code=status.HTTP_201_CREATED)
async def create_task(db: db_dependency,
                      title: str = Form(...),
                      description: str = Form(...),
                      Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter valid access token")
    
    user = Authorize.get_jwt_subject()
    current_user = db.query(User).filter(User.username==user).first() 

    new_task = Task(
        title = title,
        description = description,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return RedirectResponse(url="/task", status_code=303)
   

# Update side
@task.get('/update/{id}', status_code=status.HTTP_200_OK)
async def update_task_by_id(request: Request, id: int):
    return templates.TemplateResponse("task/task_update.html", {"request": request, "id":id})

@task.post('/update/{id}', status_code=status.HTTP_200_OK)
async def update_task_by_id(id: int,
                      db: db_dependency,
                      title: str = Form(...),
                      description: str = Form(...), 
                      Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter a valid access token")
    
    user = Authorize.get_jwt_subject()
    current_user = db.query(User).filter(User.username == user).first()

    task = db.query(Task).filter(Task.id == id).first()
    
    if task.id != id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, you can not edit/change other's task")

    task.title = title
    task.description = description
    db.commit()
    db.refresh(task)
    return RedirectResponse(url='/task', status_code=status.HTTP_303_SEE_OTHER)


# Delete side
@task.get('/delete/{id}')
async def delete_task(request: Request, db: db_dependency, id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Enter a valid access token")
    user = Authorize.get_jwt_subject()
    current_user = db.query(User).filter(User.username == user).first()
    task = db.query(Task).filter(Task.id == id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sorry, you can not delete other's task")
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/task", status_code=303)



