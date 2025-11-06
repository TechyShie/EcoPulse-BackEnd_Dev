# services/auth.py  (adjust path to match your project structure)
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate
from ..core.security import get_password_hash, verify_password, needs_rehash
import re

def generate_username(email: str, full_name: str, db: Session) -> str:
    """
    Generate a unique username from email and full name
    """
    base_username = re.sub(r'[^a-zA-Z0-9_]', '', full_name.lower().replace(' ', '_')) or email.split('@')[0]
    username = base_username

    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    return username

def create_user(db: Session, user_data: UserCreate):
    """
    Create a new user. No truncation; password is hashed via get_password_hash (Argon2).
    """
    password = user_data.password  # no truncation, no slicing

    # Generate unique username
    username = generate_username(user_data.email, user_data.full_name, db)

    hashed_password = get_password_hash(password)

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
    """
    Authenticate user. If the stored password hash is old (bcrypt) and verifies,
    re-hash with Argon2 and update the DB so the account migrates.
    """
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    # If hash needs update (e.g. was bcrypt), re-hash with current scheme and save.
    try:
        if needs_rehash(user.hashed_password):
            user.hashed_password = get_password_hash(password)
            db.add(user)
            db.commit()
            db.refresh(user)
    except Exception:
        # If rehash/update fails for some reason, don't block login — we've already verified.
        # But log the error in your real logs, here we fail silently to avoid locking real users out.
        pass

    return user

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
