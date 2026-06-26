from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import (
    declarative_base
)

from sqlalchemy.orm import sessionmaker


# =====================================
# DATABASE CONFIGURATION
# =====================================

DATABASE_URL = (

    "mysql+pymysql://root:Sai%401234@localhost/ai_pdf_assistant"
)

# =====================================
# CREATE ENGINE
# =====================================

engine = create_engine(

    DATABASE_URL
)

# =====================================
# SESSION FACTORY
# =====================================

SessionLocal = sessionmaker(

    autocommit=False,

    autoflush=False,

    bind=engine
)

# =====================================
# BASE CLASS
# =====================================

Base = declarative_base()


# =====================================
# GET DATABASE SESSION
# =====================================

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()