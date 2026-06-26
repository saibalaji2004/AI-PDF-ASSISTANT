# 🤖 AI PDF Assistant - Retrieval Augmented Generation (RAG) System

An AI-powered PDF Question Answering System built using **React, FastAPI, FAISS, Sentence Transformers, MySQL, and OpenRouter LLM**. The application enables users to upload PDF documents, ask questions in natural language, summarize documents, manage chat history, and export AI conversations with source citations.

---

# 📌 Project Overview

AI PDF Assistant is a Retrieval-Augmented Generation (RAG) based web application that allows users to interact intelligently with PDF documents.

Instead of manually searching through lengthy PDF files, users can simply ask questions in natural language and receive accurate, context-aware responses generated using semantic search and Large Language Models (LLMs). The system combines vector embeddings, FAISS similarity search, and OpenRouter LLMs to provide reliable answers with relevant document sources.

---

# ✨ Features

## 🔐 User Authentication

- User Signup
- User Login
- JWT Authentication
- Secure Session Management

---

## 📄 PDF Management

- Upload PDF Documents
- Multiple PDF Support
- Select Active PDF
- View Original PDF
- Intelligent Text Extraction

---

## 🤖 AI Chat Assistant

- Ask Questions from PDF
- Streaming AI Responses
- Context-Aware Answers
- Source Citation with Page Number & Chunk Number
- Semantic Search Based Retrieval

---

## 📚 Chat Management

- Chat History
- Search Chats
- Search by Chat Title
- Search by PDF Name
- Search by Chat Content
- Rename Chat
- Pin / Unpin Chat
- Delete Chat
- Sidebar Hide / Show

---

## 📑 PDF Summary

- Generate AI-powered summary of the selected PDF

---

## 📤 Export

- Export complete chat history as a PDF document

---

# 🏗️ System Architecture

```
                    User

                      │

                      ▼

             React Frontend (Vite)

                      │

                      ▼

              FastAPI Backend

                      │

        ┌─────────────┼─────────────┐

        ▼                           ▼

Sentence Transformer         MySQL Database

        │

        ▼

 FAISS Vector Database

        │

        ▼

 OpenRouter LLM API

        │

        ▼

 AI Generated Response

        │

        ▼

 Answer with Source Citation
```

---

# 📦 Project Modules

1. User Authentication Module
2. PDF Upload Module
3. PDF Text Extraction Module
4. Text Chunk Generation Module
5. Embedding Generation Module
6. FAISS Vector Storage Module
7. RAG Question Answering Module
8. PDF Summarization Module
9. Chat Session Management Module
10. Search & Filter Module
11. Export Chat Module
12. Sidebar Management Module

---

# 🛠️ Technology Stack

## Frontend

- React.js
- JavaScript
- CSS
- Vite

---

## Backend

- FastAPI
- Python
- SQLAlchemy

---

## Database

- MySQL

---

## Vector Database

- FAISS

---

## AI & NLP

- Sentence Transformers (all-MiniLM-L6-v2)
- FAISS Semantic Search
- OpenRouter LLM API
- Retrieval-Augmented Generation (RAG)
- Semantic Similarity Search

---

# 📂 Project Structure

```
pdf-explainer/

│

├── backend/

│   ├── routes/

│   ├── services/

│   ├── uploads/

│   ├── vector_store/

│   ├── models.py

│   ├── database.py

│   ├── main.py

│   ├── requirements.txt

│   └── .env

│

├── frontend/

│   ├── src/

│   ├── public/

│   ├── package.json

│   └── vite.config.js

│

└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```
git clone https://github.com/yourusername/AI-PDF-Assistant.git
```

---

## Backend Setup

```
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

Backend URL

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

---

## Frontend Setup

```
cd frontend

npm install

npm run dev
```

Frontend URL

```
http://localhost:5173
```

---

# 🔑 Environment Variables

Create a `.env` file inside the backend folder.

```
OPENROUTER_API_KEY=your_api_key

SECRET_KEY=your_secret_key

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=1440

MYSQL_HOST=localhost

MYSQL_USER=root

MYSQL_PASSWORD=your_password

MYSQL_DATABASE=ai_pdf_assistant
```

---

# 📌 API Endpoints

| Method | Endpoint | Description |
|------------|-----------------------------|--------------------------------|
| POST | /signup | User Registration |
| POST | /login | User Login |
| POST | /upload | Upload PDF |
| POST | /ask | Ask Question |
| POST | /ask-stream | Streaming AI Response |
| POST | /summarize | Summarize PDF |
| GET | /chat-sessions | Get User Chat Sessions |
| GET | /chat-history/{id} | Get Chat History |
| GET | /view-pdf/{pdf_name} | View Uploaded PDF |
| GET | /export-chat/{id} | Export Chat as PDF |
| PUT | /rename-session/{id} | Rename Chat Session |
| PUT | /pin-session/{id} | Pin / Unpin Chat |
| DELETE | /chat-session/{id} | Delete Chat Session |

---

# 🚀 Workflow

```
User Uploads PDF

        │

        ▼

PDF Text Extraction

        │

        ▼

Chunk Generation

        │

        ▼

Embedding Generation

        │

        ▼

FAISS Vector Storage

        │

        ▼

User Question

        │

        ▼

Semantic Similarity Search

        │

        ▼

Relevant Chunks Retrieved

        │

        ▼

OpenRouter LLM

        │

        ▼

AI Generated Answer

        │

        ▼

Answer + Source Citations
```

---

# 📸 Screenshots

Include screenshots for:

- Login Page
- Signup Page
- Dashboard
- Upload PDF
- Chat Interface
- Search Chats
- Rename Chat
- Pin Chat
- Delete Chat
- Export Chat
- PDF Summary
- Sidebar Toggle

---

# 🎯 Advantages

- Fast Semantic Vector Search
- Retrieval-Augmented Generation (RAG)
- AI-Powered PDF Question Answering
- Secure JWT Authentication
- Multi-User Support
- Real-Time Streaming Responses
- Context-Aware Retrieval
- Source Citation Support
- Chat History Management
- Export Conversations as PDF
- Modern Responsive User Interface

---

# 🔮 Future Scope

- OCR Support for Scanned PDFs
- Multi-Language PDF Support
- Voice-Based Question Answering
- AI Notes Generation
- Cloud Storage Integration
- Mobile Application
- Team Collaboration
- PDF Annotation Support

---

# 👨‍💻 Developed By

**Chimata Sai Balaji**

B.Tech Student

Siddhartha Academy of Higher Education

Department of Computer Science & Engineering

**Skills**

- Artificial Intelligence
- Machine Learning
- Full Stack Development
- Python
- FastAPI
- React

---

# 📄 License

This project is developed for educational and academic purposes.

© 2026 AI PDF Assistant - Retrieval Augmented Generation (RAG) System`