import base64
import hashlib
import hmac
import json
import os
import secrets
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated

import magic
from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile, status
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

import models
from database import Base, SessionLocal, engine


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "dataset" / "uploads"))
OUTPUT_FILE = Path(os.getenv("OUTPUT_FILE", BASE_DIR / "nb_output" / "arabic_word.txt"))
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 100 * 1024 * 1024))
SECRET_KEY = os.getenv("SECRET_KEY")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")
ENABLE_KAGGLE_ENDPOINT = os.getenv("ENABLE_KAGGLE_ENDPOINT", "false").lower() == "true"
TOKEN_EXPIRE_MINUTES = int(os.getenv("TOKEN_EXPIRE_MINUTES", "60"))
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/x-msvideo"}

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set before starting the application")

app = FastAPI(title="Arabic Lip-Reading API")
Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

configured_origins = os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in configured_origins.split(",") if origin.strip()],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-Admin-Token"],
)


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str) -> str:
    expires = int((datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)).timestamp())
    payload = json.dumps({"sub": subject, "exp": expires}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    signature = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).digest()
    return f"{encoded}.{base64.urlsafe_b64encode(signature).rstrip(b'=').decode()}"


def decode_token(token: str) -> str:
    try:
        encoded, signature = token.split(".", 1)
        expected = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).digest()
        supplied = base64.urlsafe_b64decode(signature + "=" * (-len(signature) % 4))
        if not hmac.compare_digest(expected, supplied):
            raise ValueError
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        claims = json.loads(payload)
        if claims["exp"] < int(datetime.now(timezone.utc).timestamp()):
            raise ValueError
        return claims["sub"]
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")


def current_user(token: Annotated[str, Depends(oauth2_scheme)], db: db_dependency) -> models.User:
    email = decode_token(token)
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: db_dependency):
    if db.query(models.User).filter(
        (models.User.email == user_data.email) | (models.User.username == user_data.username)
    ).first():
        raise HTTPException(status_code=409, detail="Username or email already exists")
    user = models.User(
        username=user_data.username,
        email=user_data.email,
        password=hash_password(user_data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/login")
def login(credentials: LoginRequest, db: db_dependency):
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if user is None or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_token(user.email), "token_type": "bearer"}


@app.get("/users/me", response_model=UserResponse)
def read_current_user(user: Annotated[models.User, Depends(current_user)]):
    return user


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/files")
async def upload_file(
    file: UploadFile = File(...),
    user: Annotated[models.User, Depends(current_user)] = None,
):
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=415, detail="Only supported video files are accepted")

    ensure_upload_dir()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".mp4", ".mov", ".avi"}:
        raise HTTPException(status_code=415, detail="Unsupported video extension")

    destination = UPLOAD_DIR / f"{secrets.token_hex(16)}{suffix}"
    size = 0
    content_verified = False
    try:
        with destination.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(status_code=413, detail="Uploaded file is too large")
                if not content_verified:
                    detected_type = magic.from_buffer(chunk, mime=True)
                    if detected_type not in ALLOWED_VIDEO_TYPES:
                        raise HTTPException(
                            status_code=415,
                            detail="Uploaded file content does not match an allowed video type",
                        )
                    content_verified = True
                output.write(chunk)
    except HTTPException:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()
    return {"message": "File uploaded successfully", "filename": destination.name}


@app.get("/download")
def download_file(user: Annotated[models.User, Depends(current_user)]):
    from fastapi.responses import FileResponse

    if not OUTPUT_FILE.is_file():
        raise HTTPException(status_code=404, detail="Prediction output is not available")
    return FileResponse(OUTPUT_FILE, media_type="text/plain", filename="arabic_word.txt")


@app.post("/kaggle")
async def kaggle_commands(x_admin_token: str | None = Header(default=None)):
    if not ENABLE_KAGGLE_ENDPOINT:
        raise HTTPException(status_code=404, detail="Kaggle workflow is disabled")
    if not ADMIN_TOKEN or not hmac.compare_digest(x_admin_token or "", ADMIN_TOKEN):
        raise HTTPException(status_code=403, detail="Administrator access required")

    from kaggle import run_workflow

    try:
        return await run_in_threadpool(run_workflow)
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=502, detail="Kaggle command failed")
