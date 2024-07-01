
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()



# User Model
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)  
    email = Column(String(75), unique=True)
    password = Column(Text)      
    is_staff = Column(Boolean, default=False)
    
    tasks = relationship("Task", back_populates="user")

    def __repr__(self):
        return f"<user {self.username}>"



class Task(Base):
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True)
    title = Column(String(50))
    description = Column(String)
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"<id: {self.id}, title: {self.title}>"
    
