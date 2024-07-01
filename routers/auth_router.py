import datetime
from fastapi import APIRouter, Form, Request, status, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash

from models import User
from db import db_dependency

auth = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

templates = Jinja2Templates(directory="templates")


# Register side
@auth.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse("auth/signup.html", {"request": request})

@auth.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(db: db_dependency,
                username: str = Form(...), 
                password: str = Form(...),
                email: str = Form(...), 
                is_staff: bool = Form(False)):
    db_username = db.query(User).filter(User.username == username).first()
    if db_username is not None:
        return HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail='This email already exists!')
    
    db_email = db.query(User).filter(User.email == email).first()
    if db_email is not None:
        return HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail='This username already exists!') 
    
    new_user = User(
        username = username,
        password = generate_password_hash(password),
        email = email,
        is_staff = is_staff
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/auth/login", status_code=303)


# Login side
@auth.get('/login', response_class=HTMLResponse, status_code=status.HTTP_200_OK)
async def login(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@auth.post("/login", status_code=status.HTTP_200_OK, response_class=HTMLResponse)
async def login(db: db_dependency,
                username_or_email: str = Form(...), 
                password: str = Form(...),
                Authorize: AuthJWT = Depends()):
    # query for login with username or email
    user = db.query(User).filter(
        or_(
            User.username == username_or_email,
            User.email == username_or_email
        )
    ).first()

    if user and check_password_hash(user.password, password):
        access_lifetime = datetime.timedelta(minutes=60)
        refresh_lifetime = datetime.timedelta(days=3)
        access_token = Authorize.create_access_token(subject=user.username, expires_time=access_lifetime)
        refresh_token = Authorize.create_refresh_token(subject=user.username, expires_time=refresh_lifetime)

        response = RedirectResponse(url="/task", status_code=status.HTTP_303_SEE_OTHER)
        Authorize.set_access_cookies(access_token, response)
        Authorize.set_refresh_cookies(refresh_token, response)
        return response
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid username or password")


# Create new access token via help of refresh token
@auth.post('/login/refresh')
async def refresh_token(db: db_dependency, Authorize: AuthJWT = Depends()):
    try:
        access_lifetime = datetime.timedelta(minutes=60)
        Authorize.jwt_refresh_token_required()            # valid refresh token ni talab qiladi
        user = Authorize.get_jwt_subject()      # kiritilgan refresh tokendan username ni ajratib oladi

        current_user = db.query(User).filter(User.username==user).first()
        if current_user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        new_access_token = Authorize.create_access_token(subject=current_user.username, expires_time=access_lifetime)
        response = {"access_token": new_access_token}
        return response
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Refresh token")
    
# Logout side
@auth.get("/logout", response_class=HTMLResponse)
async def logout(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    Authorize.unset_jwt_cookies()
    return RedirectResponse(url="/auth/login", status_code=302)
