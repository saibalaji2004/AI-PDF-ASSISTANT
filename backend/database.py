from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker

from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv

import os


# =====================================
# LOAD ENVIRONMENT VARIABLES
# =====================================

load_dotenv()


# =====================================
# DATABASE CONFIGURATION
# =====================================

MYSQLHOST = os.getenv("MYSQLHOST")

MYSQLPORT = os.getenv("MYSQLPORT")

MYSQLUSER = os.getenv("MYSQLUSER")

MYSQLPASSWORD = os.getenv("MYSQLPASSWORD")

MYSQLDATABASE = os.getenv("MYSQLDATABASE")


DATABASE_URL = (
    f"mysql+pymysql://{MYSQLUSER}:{MYSQLPASSWORD}"
    f"@{MYSQLHOST}:{MYSQLPORT}/{MYSQLDATABASE}"
)


# =====================================
# CREATE ENGINE
# =====================================

engine = create_engine(

    DATABASE_URL,

    pool_pre_ping=True
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