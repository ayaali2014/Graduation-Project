from operator import and_
from fastapi import FastAPI, HTTPException, Response, status
from fastapi import Depends
from fastapi.params import Path
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import FastAPI, File, UploadFile, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
#from jose import JWTError, jwt  # For JWT (not shown)
from datetime import datetime, timedelta  # For JWT (not shown)
import magic
from database import engine  # Assuming this is your database connection engine
import models
from fastapi import UploadFile
from pyngrok import ngrok
import os
#import uuid
# Start the ngrok tunnel

import subprocess
import shlex
# Fix the typo: User (uppercase U)
class User(declarative_base()):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True)
    email = Column(String(100))
    password = Column(String(50))  # Store the hashed password

# Dependency for creating database sessions (assuming 'database.py' defines engine)
def get_db():
    db = sessionmaker(autocommit=False, autoflush=False, bind=engine)()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")  # Define token URL endpoint
# JWT configuration
SECRET_KEY = "your_secret_key"  # Replace with a strong, secure secret key
ALGORITHM = "HS256"

app = FastAPI()
models.Base.metadata.create_all(bind=engine)  # Create tables if they don't exist
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
origins = [
    "http://localhost:8000", # Example origin for development
    "http://127.0.0.1:8000", # Replace with your actual domain
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserBase(BaseModel):
    username: str
    email: str
    password: str

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,param1: Optional[str] = None, param2: Optional[str] = None, param3: Optional[str] = None):
    try:
        db_user = User(
            username=param1,
            email=param2,
            password=param3
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return {"message": "User created successfully"}
    except Exception as e:  # Consider more specific exceptions for better error handling
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.get("/users/")
def read_root( db: db_dependency,param1: Optional[str] = None, param2: Optional[str] = None):
    if param1 is None or param2 is None:
        raise HTTPException(status_code=400, detail="Both email and password are required")
    
    user = db.query(User).filter(and_(User.email == param1, User.password == param2)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
#######################################################################################################
from secrets import token_hex
@app.post('/files')
async def get_file(file: UploadFile = File(...),):
    file_ex = file.filename.split(".").pop()
    file_name = token_hex(10)
    file_path = fr"C:\Users\Abdelrhman Ali\Downloads\graduation\dataset\{file_name}.{file_ex}"
    with open(file_path, "wb") as f:
        contents = await file.read()  # For FastAPI
        f.write(contents)
    return {'message': f"File '{file_path}' uploaded successfully."}


##########################################################################################################
@app.get("/download")
async def download_file():
    # Specify the file path
    file_path = r"C:\Users\Abdelrhman Ali\Downloads\graduation\nb_output\arabic_word.txt"

    # Read the file content
    with open(file_path, "r", encoding='utf-8') as file:
        file_content = file.read()

    # Return the file as a response
    return Response(
        content=file_content,
        media_type="text/plain",
        headers={
            "Content-Disposition": f"attachment; filename=file.txt"
        }
    )

###############################################################################################################
###################################### kaggle ###############################################################
def execute_terminal_command(command):
    # Execute the command
    command_list = shlex.split(command)
    result = subprocess.run(command_list, shell=True, text=True, capture_output=True)
    # Print the output of the command
    return result.stdout


def pull_kaggle_dataset():
    command = fr'kaggle datasets metadata -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset" "ayaali2002/gbDataset"'
    return execute_terminal_command(command)


def update_kaggle_dataset():
    command = fr'kaggle datasets version -p "C:\Users\Abdelrhman Ali\Downloads\graduation\dataset" -m "dataset using kaggle API 2024" -r tar'
    return execute_terminal_command(command)


def push_kaggle_notebook():
    command = fr'kaggle kernels push -p "C:\Users\Abdelrhman Ali\Downloads\graduation\notebook"'
    return execute_terminal_command(command)


def get_notebook_status():
    command = fr'kaggle kernels status "ayaali2002/final-nb"'
    return execute_terminal_command(command)


def get_notebook_output():
    command = fr'kaggle kernels output "ayaali2002/final-nb" -p "C:\Users\Abdelrhman Ali\Downloads\graduation\nb_output"'
    return execute_terminal_command(command)



@app.get("/kaggle")
async def kaggle_commands():
    pull_ds = await pull_kaggle_dataset()
    print(pull_ds)
    update_ds = await update_kaggle_dataset()
    print(update_ds)
    push_nb = await push_kaggle_notebook()
    print(push_nb)
    status = await get_notebook_status()
    if("complete" in status):
        get_notebook_output()   


