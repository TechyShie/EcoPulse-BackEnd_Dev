from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password
import re

def generate_username(email: str, full_name: str, db: Session) -> str:
    """
    Generate a unique username from email and full name
    """
    # Try using full name first
    base_username = re.sub(r'[^a-zA-Z0-9_]', '', full_name.lower().replace(' ', '_'))
    username = base_username
    
    # Check if username exists and append numbers if needed
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    return username

def create_user(db: Session, user_data: UserCreate):
    # Generate unique username
    username = generate_username(user_data.email, user_data.full_name, db)
    
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        username=username,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()