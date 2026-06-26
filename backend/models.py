
from sqlalchemy import (

    Column,

    Integer,

    String,

    Text,

    ForeignKey,

    TIMESTAMP,

    Boolean
)

from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from database import Base


# =====================================
# USER MODEL
# =====================================

class User(Base):

    __tablename__ = "users"

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )

    username = Column(

        String(255),

        unique=True
    )

    email = Column(

        String(255),

        unique=True
    )

    password = Column(

        String(255)
    )

    created_at = Column(

        TIMESTAMP,

        server_default=func.now()
    )

    # =================================
    # Relationships
    # =================================

    sessions = relationship(

        "ChatSession",

        back_populates="user",

        cascade="all, delete"
    )


# =====================================
# CHAT SESSION MODEL
# =====================================

class ChatSession(Base):

    __tablename__ = "chat_sessions"

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )

    user_id = Column(

        Integer,

        ForeignKey(
            "users.id"
        ),

        nullable=True
    )

    pdf_name = Column(

        String(255)
    )

    # =================================
    # NEW SESSION TITLE COLUMN
    # =================================

    title = Column(

        String(255),

        nullable=True
    )

    is_pinned = Column(

        Boolean,

        default=False
    )

    created_at = Column(

        TIMESTAMP,

        server_default=func.now()
    )

    # =================================
    # Relationships
    # =================================

    user = relationship(

        "User",

        back_populates="sessions"
    )

    messages = relationship(

        "ChatMessage",

        back_populates="session",

        cascade="all, delete"
    )


# =====================================
# CHAT MESSAGE MODEL
# =====================================

class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(

        Integer,

        primary_key=True,

        index=True
    )

    session_id = Column(

        Integer,

        ForeignKey(
            "chat_sessions.id"
        )
    )

    role = Column(

        String(50)
    )

    message = Column(

        Text
    )

    created_at = Column(

        TIMESTAMP,

        server_default=func.now()
    )

    # =================================
    # Relationships
    # =================================

    session = relationship(

        "ChatSession",

        back_populates="messages"
    )

