import faiss
import json
import numpy as np
import os
import httpx
import traceback

from pathlib import Path

from dotenv import load_dotenv

from sentence_transformers import (
    SentenceTransformer
)

from openai import OpenAI

from rank_bm25 import BM25Okapi


# =====================================
# Load Environment Variables
# =====================================

env_path = (

    Path(__file__).resolve().parent.parent

    / ".env"
)

load_dotenv(
    dotenv_path=env_path
)

# =====================================
# OpenRouter API Key
# =====================================
api_key = (
    os.getenv("OPENROUTER_API_KEY", "")
    .strip()
    .replace("\n", "")
    .replace("\r", "")
)

print("="*60)
print("OPENROUTER API KEY FOUND :", api_key is not None)

if api_key:
    print("API KEY LENGTH :", len(api_key))
    print("FIRST 10 CHARS :", api_key[:10])

print("="*60)

print(
    "OpenRouter API Key Loaded"
)

# =====================================
# OpenRouter Client
# =====================================


client = OpenAI(

    api_key=api_key,

    base_url="https://openrouter.ai/api/v1",

    http_client=httpx.Client(
        timeout=60.0
    ),

    default_headers={
        "HTTP-Referer": "https://ai-pdf-assistant-production.up.railway.app",
        "X-Title": "AI PDF Assistant"
    }
)
# =====================================
# Embedding Model
# =====================================
# =====================================
# Lazy Loading Embedding Model
# =====================================

embedding_model = None


def get_embedding_model():

    global embedding_model

    if embedding_model is None:

        print("Loading Embedding Model...")

        embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return embedding_model

# =====================================
# Similarity Threshold
# =====================================

SIMILARITY_THRESHOLD = 1.5


# =====================================
# Hybrid Retrieval Function
# =====================================

def retrieve_relevant_chunks(

    question,

    selected_pdf,

    user_id,

    top_k=10,

    max_chunks=4
):

    # =================================
    # Load FAISS Index
    # =================================

    index = faiss.read_index(

        "vector_store/faiss_index.bin"
    )

    # =================================
    # Load Metadata
    # =================================

    with open(

        "vector_store/metadata.json",

        "r",

        encoding="utf-8"

    ) as f:

        metadata = json.load(f)

    # =================================
    # Filter Selected PDF + User
    # =================================

    pdf_chunks = []

    for item in metadata:

        if (

            item["pdf_file"]

            ==

            selected_pdf

            and

            item.get("user_id")

            ==

            user_id
        ):

            pdf_chunks.append(item)

    # =================================
    # No Chunks
    # =================================

    if len(pdf_chunks) == 0:

        return [], []

    # =================================
    # BM25
    # =================================

    tokenized_chunks = [

        chunk["text"].lower().split()

        for chunk in pdf_chunks
    ]

    bm25 = BM25Okapi(
        tokenized_chunks
    )

    tokenized_query = (
        question.lower().split()
    )

    bm25_scores = bm25.get_scores(
        tokenized_query
    )

    # =================================
    # Generate Embedding
    # =================================

    question_embedding = (

        get_embedding_model().encode(question)
    )

    question_embedding = np.array(

        [question_embedding]

    ).astype("float32")

    # =================================
    # FAISS Search
    # =================================

    distances, indices = index.search(

        question_embedding,

        top_k
    )

    # =================================
    # Combined Results
    # =================================

    combined_results = []

    used_chunks = set()

    # =================================
    # FAISS Results
    # =================================

    for rank, idx in enumerate(indices[0]):

        chunk_data = metadata[idx]

        distance = distances[0][rank]

        if distance > SIMILARITY_THRESHOLD:

            continue

        # =================================
        # USER FILTER
        # =================================

        if (

            chunk_data["pdf_file"]

            !=

            selected_pdf
        ):

            continue

        if (

            chunk_data.get("user_id")

            !=

            user_id
        ):

            continue

        combined_results.append({

            "text":
            chunk_data["text"],

            "page_number":
            chunk_data["page_number"],

            "chunk_number":
            chunk_data["chunk_number"],

            "pdf_file":
            chunk_data["pdf_file"],

            "score":
            float(1 / (distance + 0.01))
        })

    # =================================
    # BM25 Results
    # =================================

    for i, score in enumerate(bm25_scores):

        chunk_data = pdf_chunks[i]

        combined_results.append({

            "text":
            chunk_data["text"],

            "page_number":
            chunk_data["page_number"],

            "chunk_number":
            chunk_data["chunk_number"],

            "pdf_file":
            chunk_data["pdf_file"],

            "score":
            float(score)
        })

    # =================================
    # Sort Results
    # =================================

    combined_results = sorted(

        combined_results,

        key=lambda x: x["score"],

        reverse=True
    )

    # =================================
    # Final Chunks
    # =================================

    retrieved_chunks = []

    retrieved_sources = []

    for item in combined_results:

        chunk_key = (

            item["page_number"],

            item["chunk_number"]
        )

        if chunk_key in used_chunks:

            continue

        used_chunks.add(chunk_key)

        retrieved_chunks.append(

            item["text"]
        )

        retrieved_sources.append({

            "page_number":
            item["page_number"],

            "chunk_number":
            item["chunk_number"],

            "pdf_file":
            item["pdf_file"]
        })

        if len(retrieved_chunks) >= max_chunks:

            break

    return (

        retrieved_chunks,

        retrieved_sources
    )


# =====================================
# Ask Question
# =====================================

def ask_question(

    question,

    selected_pdf,

    user_id,

    chat_history=[]
):

    retrieved_chunks, retrieved_sources = (

        retrieve_relevant_chunks(

            question,

            selected_pdf,

            user_id
        )
    )

    if len(retrieved_chunks) == 0:

        return {

            "question":
            question,

            "answer":
            "I could not find the answer in the document.",

            "sources":
            []
        }

    context = "\n\n".join(
        retrieved_chunks
    )

    history_text = ""

    for message in chat_history:

        role = message.get(
            "role",
            "user"
        )

        text = message.get(
            "text",
            ""
        )

        history_text += (
            f"{role}: {text}\n"
        )

    prompt = f"""
You are an intelligent AI PDF assistant.

STRICT RULES:

1. Answer ONLY using document context
2. Be concise and accurate
3. Avoid repetition
4. Do NOT hallucinate

ACTIVE PDF:
{selected_pdf}

CHAT HISTORY:
{history_text}

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}
"""

    try:

        response = client.chat.completions.create(


            model="meta-llama/llama-3.1-8b-instruct:free",

            messages=[
                {
                    "role": "user",

                    "content": prompt
                }
            ]
        )

        answer = (

            response
            .choices[0]
            .message.content
        )

    except Exception as e:

        print(traceback.format_exc())

        answer = (
            f"LLM Error: {repr(e)}"
        )

    return {

        "question":
        question,

        "answer":
        answer,

        "retrieved_chunks":
        retrieved_chunks,

        "sources":
        retrieved_sources
    }


# =====================================
# Summarize PDF
# =====================================

def summarize_pdf(

    selected_pdf,

    user_id
):

    with open(

        "vector_store/metadata.json",

        "r",

        encoding="utf-8"

    ) as f:

        metadata = json.load(f)

    pdf_chunks = []

    for item in metadata:

        if (

            item["pdf_file"]

            ==

            selected_pdf

            and

            item.get("user_id")

            ==

            user_id
        ):

            pdf_chunks.append(

                item["text"]
            )

    if len(pdf_chunks) == 0:

        return {

            "summary":
            "No content found."
        }

    document_text = "\n\n".join(
        pdf_chunks
    )

    document_text = document_text[:12000]

    prompt = f"""
Generate a concise summary
of this PDF.

Requirements:
- Avoid repetition
- Explain important topics
- Use simple language
- Use bullet points

PDF:
{selected_pdf}

CONTENT:
{document_text}
"""

    try:

        response = client.chat.completions.create(


            model="meta-llama/llama-3.1-8b-instruct:free",

            messages=[
                {
                    "role": "user",

                    "content": prompt
                }
            ]
        )

        summary = (

            response
            .choices[0]
            .message.content
        )

    except Exception as e:

        print(traceback.format_exc())

        summary = (
            f"Summary Error: {repr(e)}"
        )

    return {

        "pdf":
        selected_pdf,

        "summary":
        summary
    }


# =====================================
# Stream Answer
# =====================================

def stream_answer(

    question,

    selected_pdf,

    user_id,

    chat_history=[]
):

    retrieved_chunks, _ = (

        retrieve_relevant_chunks(

            question,

            selected_pdf,

            user_id
        )
    )

    if len(retrieved_chunks) == 0:

        yield "I could not find the answer in the document."

        return

    context = "\n\n".join(
        retrieved_chunks
    )

    history_text = ""

    for message in chat_history:

        role = message.get(
            "role",
            "user"
        )

        text = message.get(
            "text",
            ""
        )

        history_text += (
            f"{role}: {text}\n"
        )

    prompt = f"""
You are an intelligent AI PDF assistant.

STRICT RULES:

1. Answer ONLY using document context
2. Be concise
3. Avoid repetition
4. Do NOT hallucinate

ACTIVE PDF:
{selected_pdf}

CHAT HISTORY:
{history_text}

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}
"""

    try:

        stream = client.chat.completions.create(


            model="meta-llama/llama-3.1-8b-instruct:free",

            messages=[
                {
                    "role": "user",

                    "content": prompt
                }
            ],

            stream=True
        )

        for chunk in stream:

            delta = (

                chunk
                .choices[0]
                .delta
            )

            if (

                hasattr(delta, "content")

                and

                delta.content
            ):

                yield delta.content

    except Exception as e:
        print(traceback.format_exc())

        yield f"\nStreaming Error: {repr(e)}"