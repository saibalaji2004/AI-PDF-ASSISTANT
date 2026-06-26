from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

# =====================================
# Import PDF Routes
# =====================================

from routes.pdf_routes import (
    router as pdf_router
)

# =====================================
# Import Auth Routes
# =====================================

from routes.auth_routes import (
    router as auth_router
)

# =====================================
# Database Imports
# =====================================

from database import (

    engine,

    Base
)

import models

# =====================================
# Create Database Tables
# =====================================

Base.metadata.create_all(

    bind=engine
)

# =====================================
# FastAPI App
# =====================================

app = FastAPI()

# =====================================
# CORS Configuration
# =====================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)

# =====================================
# Include PDF Routes
# =====================================

app.include_router(

    pdf_router
)

# =====================================
# Include Auth Routes
# =====================================

app.include_router(

    auth_router
)

# =====================================
# Root Route
# =====================================

@app.get("/")

async def home():

    return {

        "message":
        "AI PDF Assistant API Running"
    }