from passlib.context import CryptContext

from jose import jwt

from jose.exceptions import JWTError

from datetime import (

    datetime,

    timedelta
)

from fastapi import (

    Header,

    HTTPException
)

from database import SessionLocal

from models import User

# =====================================
# SECRET KEY
# =====================================

SECRET_KEY = "AI_PDF_ANSWER_SUPER_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# =====================================
# PASSWORD HASHING
# =====================================

pwd_context = CryptContext(

    schemes=["bcrypt"],

    deprecated="auto"
)

# =====================================
# HASH PASSWORD
# =====================================

def hash_password(

    password
):

    return pwd_context.hash(
        password
    )

# =====================================
# VERIFY PASSWORD
# =====================================

def verify_password(

    plain_password,

    hashed_password
):

    return pwd_context.verify(

        plain_password,

        hashed_password
    )

# =====================================
# CREATE ACCESS TOKEN
# =====================================

def create_access_token(

    data: dict
):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(

        minutes=
        ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({

        "exp":
        expire
    })

    encoded_jwt = jwt.encode(

        to_encode,

        SECRET_KEY,

        algorithm=ALGORITHM
    )

    return encoded_jwt

# =====================================
# VERIFY TOKEN
# =====================================

def verify_token(

    token: str
):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:

        return None

# =====================================
# GET CURRENT USER
# =====================================

def get_current_user(

    authorization: str = Header(None)
):

    # =================================
    # Check Header
    # =================================

    if not authorization:

        raise HTTPException(

            status_code=401,

            detail="Authorization token missing"
        )

    # =================================
    # Extract Token
    # =================================

    try:

        token = authorization.split(

            " "
        )[1]

    except:

        raise HTTPException(

            status_code=401,

            detail="Invalid token format"
        )

    # =================================
    # Decode Token
    # =================================

    payload = verify_token(token)

    if not payload:

        raise HTTPException(

            status_code=401,

            detail="Invalid or expired token"
        )

    # =================================
    # Extract User ID
    # =================================

    user_id = payload.get(
        "user_id"
    )

    if not user_id:

        raise HTTPException(

            status_code=401,

            detail="User ID missing"
        )

    # =================================
    # Database Lookup
    # =================================

    db = SessionLocal()

    user = db.query(User).filter(

        User.id == user_id

    ).first()

    db.close()

    if not user:

        raise HTTPException(

            status_code=401,

            detail="User not found"
        )

    return user