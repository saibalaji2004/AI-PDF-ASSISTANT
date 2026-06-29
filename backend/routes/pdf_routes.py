from services.pdf_export_service import export_chat_pdf
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import shutil
import os

# =====================================
# Database
# =====================================
from database import get_db
from models import ChatSession, ChatMessage

# =====================================
# Auth Service
# =====================================
from services.auth_service import get_current_user

# =====================================
# PDF Extraction Service
# =====================================
from services.pdf_service import extract_text_from_pdf

# =====================================
# Chunking Service
# =====================================
from services.chunk_service import create_chunks

# =====================================
# Embedding Service
# =====================================
from services.embedding_service import generate_embeddings

# =====================================
# Vector Database Service
# =====================================
from services.vector_service import create_vector_store

# =====================================
# RAG Service
# =====================================
from services.rag_service import ask_question, summarize_pdf, stream_answer

# =====================================
# Router Initialization
# =====================================
router = APIRouter()

# =====================================
# Upload Folder
# =====================================
UPLOAD_FOLDER = "uploads/pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# =====================================
# Request Model
# =====================================
class QuestionRequest(BaseModel):
    question: str = ""
    selected_pdf: str
    chat_history: list = []
    session_id: int | None = None

# =====================================
# Upload PDF Route
# =====================================
@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):

    if not file.filename.endswith(".pdf"):
        return {
            "status": "error",
            "message": "Only PDF files are allowed"
        }

    user_folder = os.path.join(
        UPLOAD_FOLDER,
        str(current_user.id)
    )

    os.makedirs(
        user_folder,
        exist_ok=True
    )

    file_path = os.path.join(
        user_folder,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    print(f"\nPDF Uploaded : {file.filename}")

    extracted_pages = extract_text_from_pdf(
        file_path
    )

    chunks = create_chunks(
        extracted_pages,
        file.filename
    )

    embedded_chunks = generate_embeddings(
        chunks,
        current_user.id
    )

    vector_result = create_vector_store(
        embedded_chunks
    )

    return {
        "status": "success",
        "message": "PDF fully processed successfully",
        "uploaded_pdf": file.filename,
        "total_pages": len(extracted_pages),
        "total_chunks": len(chunks),
        "total_embeddings": len(embedded_chunks),
        "vector_store": vector_result
    }


# =====================================
# Ask Question Route
# =====================================
@router.post("/ask")
async def ask_pdf_question(
    request: QuestionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    # =====================================
    # Create Chat Session if Needed
    # =====================================

    if request.session_id is None or request.session_id == 0:

        session_title = (
            request.question[:255]
            if request.question
            else request.selected_pdf
        )

        new_session = ChatSession(
            pdf_name=request.selected_pdf,
            title=session_title,
            user_id=current_user.id
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        session_id = new_session.id

    else:

        session_id = request.session_id

    # =====================================
    # Ask AI
    # =====================================

    result = ask_question(
        request.question,
        request.selected_pdf,
        current_user.id,
        request.chat_history
    )

    # =====================================
    # Save User Message
    # =====================================

    user_message = ChatMessage(
        session_id=session_id,
        role="user",
        message=request.question
    )

    # =====================================
    # Save AI Message
    # =====================================

    ai_message = ChatMessage(
        session_id=session_id,
        role="ai",
        message=result["answer"]
    )

    db.add(user_message)
    db.add(ai_message)

    db.commit()

    result["session_id"] = session_id

    return result


# =====================================
# Streaming Ask Route
# =====================================
@router.post("/ask-stream")
async def ask_pdf_question_stream(
    request: QuestionRequest,
    current_user=Depends(get_current_user)
):

    generator = stream_answer(
        request.question,
        request.selected_pdf,
        current_user.id,
        request.chat_history
    )

    return StreamingResponse(
        generator,
        media_type="text/plain"
    )


# =====================================
# Summarize PDF Route
# =====================================
@router.post("/summarize")
async def summarize_selected_pdf(
    request: QuestionRequest,
    current_user=Depends(get_current_user)
):

    return summarize_pdf(
        request.selected_pdf,
        current_user.id
    )


# =====================================
# View PDF
# =====================================
@router.get("/view-pdf/{pdf_name}")
async def view_pdf(pdf_name: str):

    for folder in os.listdir(UPLOAD_FOLDER):

        possible_path = os.path.join(
            UPLOAD_FOLDER,
            folder,
            pdf_name
        )

        if os.path.exists(possible_path):

            return FileResponse(
                possible_path,
                media_type="application/pdf"
            )

    return {
        "error": "PDF not found"
    }


# =====================================
# Chat Sessions
# =====================================
@router.get("/chat-sessions")
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.user_id == current_user.id
        )
        .order_by(
            ChatSession.is_pinned.desc(),
            ChatSession.created_at.desc()
        )
        .all()
    )

    results = []

    for session in sessions:

        messages = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.session_id == session.id
            )
            .all()
        )

        search_text = " ".join(
            [msg.message for msg in messages]
        )

        results.append({

            "id": session.id,

            "title": session.title,

            "pdf_name": session.pdf_name,

            "is_pinned": session.is_pinned,

            "created_at": session.created_at,

            "search_text": search_text

        })

    return results


# =====================================
# Chat History
# =====================================
@router.get("/chat-history/{session_id}")
async def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = (

        db.query(ChatSession)

        .filter(

            ChatSession.id == session_id,

            ChatSession.user_id == current_user.id

        )

        .first()

    )

    if not session:

        return {

            "error": "Unauthorized access"

        }

    messages = (

        db.query(ChatMessage)

        .filter(

            ChatMessage.session_id == session_id

        )

        .order_by(

            ChatMessage.created_at.asc()

        )

        .all()

    )

    formatted_messages = [

        {

            "role": msg.role,

            "text": msg.message,

            "sources": []

        }

        for msg in messages

    ]

    return {

        "session_id": session_id,

        "messages": formatted_messages

    }


# =====================================
# Export Chat
# =====================================
@router.get("/export-chat/{session_id}")
async def export_chat(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = (

        db.query(ChatSession)

        .filter(

            ChatSession.id == session_id,

            ChatSession.user_id == current_user.id

        )

        .first()

    )

    if not session:

        return {

            "error": "Unauthorized access"

        }

    messages = (

        db.query(ChatMessage)

        .filter(

            ChatMessage.session_id == session_id

        )

        .order_by(

            ChatMessage.created_at.asc()

        )

        .all()

    )

    os.makedirs(
        "exports",
        exist_ok=True
    )

    output_path = (
        f"exports/chat_session_{session_id}.pdf"
    )

    export_chat_pdf(

        session.title or session.pdf_name,

        session.pdf_name,

        messages,

        output_path

    )

    return FileResponse(

        output_path,

        filename=f"chat_session_{session_id}.pdf",

        media_type="application/pdf"

    )


# =====================================
# Delete Session
# =====================================
@router.delete("/chat-session/{session_id}")
async def delete_chat_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = (

        db.query(ChatSession)

        .filter(

            ChatSession.id == session_id,

            ChatSession.user_id == current_user.id

        )

        .first()

    )

    if not session:

        return {

            "error": "Session not found"

        }

    db.delete(session)

    db.commit()

    return {

        "message": "Session deleted successfully"

    }


# =====================================
# Pin Session
# =====================================
@router.put("/pin-session/{session_id}")
async def pin_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = (

        db.query(ChatSession)

        .filter(

            ChatSession.id == session_id,

            ChatSession.user_id == current_user.id

        )

        .first()

    )

    if not session:

        return {

            "error": "Session not found"

        }

    session.is_pinned = not session.is_pinned

    db.commit()

    db.refresh(session)

    return {

        "message": "Session updated",

        "is_pinned": session.is_pinned

    }


# =====================================
# Rename Session
# =====================================
@router.put("/rename-session/{session_id}")
async def rename_session(
    session_id: int,
    request: dict,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    session = (

        db.query(ChatSession)

        .filter(

            ChatSession.id == session_id,

            ChatSession.user_id == current_user.id

        )

        .first()

    )

    if not session:

        return {

            "error": "Session not found"

        }

    session.title = request.get(

        "title",

        session.title

    )

    db.commit()

    db.refresh(session)

    return {

        "message": "Session renamed successfully",

        "title": session.title

    }