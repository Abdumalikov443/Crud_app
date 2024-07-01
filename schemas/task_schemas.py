from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskModel(BaseModel):
    title: str
    description: str

    class Config:
        orm_mode = True
        json_schema_extra = {
            'example': {
                'title': 'Project on flask',
                'description': 'Learn a flask framework and try to build a pet-project for the beginning'
            }
        }

     