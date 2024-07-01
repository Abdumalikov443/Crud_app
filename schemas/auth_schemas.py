from pydantic import BaseModel


class SignUpModel(BaseModel):
    username: str
    email: str
    password: str
    is_staff: bool = False

    # Example
    class Config:           
        orm_mode = True     
        json_schema_extra = {
            'example': {
                'username': "admin", 
                'email': 'admin@gmail.com',
                'password': 'password12345',
                'is_staff': 'True',
            }
        }


class Settings(BaseModel):
    authjwt_secret_key: str = "1338d7aa813513d29245e24b585126fd11cb203aa2ba5434d4deb92d7ddfffc3"
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False


class LoginModel(BaseModel):
    username_or_email: str
    password: str