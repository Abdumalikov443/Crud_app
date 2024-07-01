from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_jwt_auth import AuthJWT

from routers.task_router import task
from routers.auth_router import auth
from schemas.auth_schemas import Settings


@AuthJWT.load_config
def get_config():
    return Settings()


app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(auth)
app.include_router(task)




@app.get('/', response_class=HTMLResponse)
async def welcome(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

