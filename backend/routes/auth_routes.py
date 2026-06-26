from fastapi import (

    APIRouter,

    Depends,

    HTTPException
)

from sqlalchemy.orm import Session

from pydantic import BaseModel

# =====================================
# Database
# =====================================

from database import get_db

from models import User

# =====================================
# Auth Service
# =====================================

from services.auth_service import (

    hash_password,

    verify_password,

    create_access_token
)

# =====================================
# Router
# =====================================

router = APIRouter()

# =====================================
# Request Models
# =====================================

class SignupRequest(BaseModel):

    username: str

    email: str

    password: str


class LoginRequest(BaseModel):

    email: str

    password: str


# =====================================
# SIGNUP ROUTE
# =====================================

@router.post("/signup")

async def signup(

    request: SignupRequest,

    db: Session = Depends(get_db)
):

    # =================================
    # Check Existing Email
    # =================================

    existing_user = db.query(

        User

    ).filter(

        User.email ==
        request.email

    ).first()

    if existing_user:

        raise HTTPException(

            status_code=400,

            detail="Email already exists"
        )

    # =================================
    # Hash Password
    # =================================

    hashed_password = hash_password(

        request.password
    )

    # =================================
    # Create User
    # =================================

    new_user = User(

        username=request.username,

        email=request.email,

        password=hashed_password
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    # =================================
    # Create Token
    # =================================

    token = create_access_token({

        "user_id":
        new_user.id,

        "email":
        new_user.email
    })

    return {

        "message":
        "User created successfully",

        "token":
        token,

        "user": {

            "id":
            new_user.id,

            "username":
            new_user.username,

            "email":
            new_user.email
        }
    }


# =====================================
# LOGIN ROUTE
# =====================================

@router.post("/login")

async def login(

    request: LoginRequest,

    db: Session = Depends(get_db)
):

    # =================================
    # Find User
    # =================================

    user = db.query(

        User

    ).filter(

        User.email ==
        request.email

    ).first()

    if not user:

        raise HTTPException(

            status_code=401,

            detail="Invalid email or password"
        )

    # =================================
    # Verify Password
    # =================================

    valid_password = verify_password(

        request.password,

        user.password
    )

    if not valid_password:

        raise HTTPException(

            status_code=401,

            detail="Invalid email or password"
        )

    # =================================
    # Generate Token
    # =================================

    token = create_access_token({

        "user_id":
        user.id,

        "email":
        user.email
    })

    return {

        "message":
        "Login successful",

        "token":
        token,

        "user": {

            "id":
            user.id,

            "username":
            user.username,

            "email":
            user.email
        }
    }