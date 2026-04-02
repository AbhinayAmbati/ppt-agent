from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker
from pydantic import BaseModel
from typing import Optional
import logging

from models import Base, User, Session as DBSession, PPTJob, engine, init_db
from db import hash_password, verify_password
from auth import create_access_token, verify_access_token
from auth.schemas import TokenResponse as Token
from agent_engine import init_agent, agent_engine
from mcp_client import mcp_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auto-PPT Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (can be restricted to frontend URL in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class PPTCreateRequest(BaseModel):
    prompt: str

class PPTCreateResponse(BaseModel):
    status: str
    file_path: Optional[str] = None
    num_slides: Optional[int] = None
    message: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    init_db()
    init_agent()
    logger.info("App started")

@app.on_event("shutdown")
async def shutdown_event():
    await mcp_client.shutdown()

@app.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username exists")
    
    user = User(username=request.username, email=request.email, hashed_password=hash_password(request.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"status": "success", "user_id": user.id}

@app.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.id)
    session = DBSession(user_id=user.id, token=token, expires_at=None)
    db.add(session)
    db.commit()
    
    return Token(access_token=token, token_type="bearer")

async def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth")
    
    token = authorization.split(" ")[1]
    token_data = verify_access_token(token)
    
    if not token_data or not token_data.sub:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    return user

@app.post("/create-ppt")
async def create_ppt(request: PPTCreateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        job = PPTJob(user_id=current_user.id, prompt=request.prompt, status="processing")
        db.add(job)
        db.commit()
        
        result = await agent_engine.create_presentation(request.prompt, mcp_client)
        
        if result["status"] == "success":
            job.status = "completed"
            job.file_path = result.get("file_path")
        else:
            job.status = "failed"
            job.error_message = result.get("message")
        
        db.commit()
        return PPTCreateResponse(**result)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if "job" in locals():
            job.status = "failed"
            job.error_message = str(e)
            db.commit()
        return PPTCreateResponse(status="error", message=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
