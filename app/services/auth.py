from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.schemas import UserCreate, UserLogin, Token, UserResponse
from app.database import users as db_users
from app.database import audit as db_audit
from app.utils.auth import hash_password, verify_password, create_access_token

def register_user_service(db: Session, user_in: UserCreate) -> UserResponse:
    existing_user = db_users.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )

    existing_email = db_users.get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    hashed_pwd = hash_password(user_in.password)
    user = db_users.create_user(db, user_in, hashed_pwd)

    db_audit.create_audit_entry(
        db,
        action="USER_REGISTER",
        entity_type="User",
        user_id=user.id,
        username=user.username,
        details=f"User registered with role {user.role}"
    )

    return UserResponse.model_validate(user)

def authenticate_user_service(db: Session, credentials: UserLogin) -> Token:
    user = db_users.get_user_by_username(db, credentials.username)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": user.username, "role": user.role, "id": user.id})

    db_audit.create_audit_entry(
        db,
        action="USER_LOGIN",
        entity_type="User",
        user_id=user.id,
        username=user.username,
        details="User logged in successfully"
    )

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )
