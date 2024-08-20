
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Enum, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import enum

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User model
class UserStatus(str, enum.Enum):
    active = "active"
    blocked = "blocked"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    status = Column(Enum(UserStatus))

# Log model
class LogLevel(str, enum.Enum):
    low = "Low"
    med = "Med"
    high = "High"
    info = "Info"
    error = "Error"

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(TIMESTAMP)
    resource_name = Column(String)
    category = Column(String)
    message = Column(Text)
    level = Column(Enum(LogLevel))

# Create tables
Base.metadata.create_all(bind=engine)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Serve HTML files
@app.get("/", response_class=HTMLResponse)
def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/admin_dashboard", response_class=HTMLResponse)
def get_admin_dashboard(request: Request):
    return templates.TemplateResponse("admin_dashboard.html", {"request": request})

@app.get("/user_profile", response_class=HTMLResponse)
def get_user_profile(request: Request):
    return templates.TemplateResponse("user_profile.html", {"request": request})

@app.get("/logs", response_class=HTMLResponse)
def get_logs(request: Request):
    return templates.TemplateResponse("logs.html", {"request": request})

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    status: UserStatus

class LogCreate(BaseModel):
    resource_name: str
    category: str
    message: str
    level: LogLevel

class LogResponse(BaseModel):
    id: int
    date: str
    resource_name: str
    category: str
    message: str
    level: LogLevel

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# User registration endpoint
@app.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(email=user.email, username=user.username, password=hashed_password, status=UserStatus.active)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Pydantic model for login request
class UserLogin(BaseModel):
    username: str
    password: str

# User login endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if db_user.status == UserStatus.blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    return {"message": "Login successful"}

# Fetch users endpoint
@app.get("/users", response_model=List[UserResponse])
def get_users(query: str = None, db: Session = Depends(get_db)):
    if query:
        users = db.query(User).filter(User.username.contains(query)).all()
    else:
        users = db.query(User).all()
    print(users)
    return users

# Fetch logs endpoint
@app.get("/logs", response_model=List[LogResponse])
def get_logs(query: str = None, db: Session = Depends(get_db)):
    if query:
        logs = db.query(Log).filter(Log.message.contains(query)).all()
    else:
        logs = db.query(Log).all()
    return logs


