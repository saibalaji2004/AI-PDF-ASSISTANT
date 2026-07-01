import faiss
import json
import numpy as np
import os
import httpx
import traceback
import time
import logging

from pathlib import Path

from dotenv import load_dotenv

from sentence_transformers import (
    SentenceTransformer
)

from openai import (
    OpenAI,
    RateLimitError,
    NotFoundError,
    APIConnectionError
)

import google.generativeai as genai

from groq import Groq

from rank_bm25 import BM25Okapi


# =====================================
# Logging Configuration
# =====================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


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
# API Keys
# =====================================
OPENROUTER_API_KEY = (
    os.getenv("OPENROUTER_API_KEY", "")
    .strip()
    .replace("\n", "")
    .replace("\r", "")
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GROQ_API_KEY = os.getenv(
    "GROQ_API_KEY"
)

logger.info("=" * 60)
logger.info(f"OPENROUTER API KEY FOUND : {OPENROUTER_API_KEY is not None}")

if OPENROUTER_API_KEY:
    logger.info(f"API KEY LENGTH : {len(OPENROUTER_API_KEY)}")
    logger.info(f"FIRST 10 CHARS : {OPENROUTER_API_KEY[:10]}")

logger.info("=" * 60)

logger.info("OpenRouter API Key Loaded")

if not OPENROUTER_API_KEY:
    raise Exception("OPENROUTER_API_KEY not found")

# =====================================
# Configure Gemini
# =====================================

if GEMINI_API_KEY:

    genai.configure(
        api_key=GEMINI_API_KEY
    )

# =====================================
# OpenRouter Models (with fallback)
# =====================================

MODELS = [

    "google/gemma-4-31b-it:free",

    "meta-llama/llama-3.3-70b-instruct:free",

    "cohere/north-mini-code:free",

    "liquid/lfm-2.5-1.2b-thinking:free"

]

# =====================================
# OpenRouter Client
# =====================================


openrouter_client = OpenAI(

    api_key=OPENROUTER_API_KEY,

    base_url="https://openrouter.ai/api/v1",

    http_client=httpx.Client(
        timeout=84.0
    ),

    default_headers={
        "HTTP-Referer": "https://ai-pdf-assistant-production.up.railway.app",
        "X-Title": "AI PDF Assistant"
    }
)

# =====================================
# Groq Client
# =====================================

groq_client = None

if GROQ_API_KEY:

    groq_client = Groq(
        api_key=GROQ_API_KEY
    )


# =====================================
# Gemini Call
# =====================================

def call_gemini(
    messages
):

    logger.info("=" * 60)
    logger.info("Provider : Gemini")
    logger.info("=" * 60)

    model = genai.GenerativeModel(
        "gemini-2.5-flash"
    )

    response = model.generate_content(

        messages[-1]["content"]

    )

    return response.text


# =====================================
# Groq Call
# =====================================

def call_groq(
    messages
):

    logger.info("=" * 60)
    logger.info("Provider : Groq")
    logger.info("=" * 60)

    response = groq_client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=messages,

        temperature=0.2

    )

    return response.choices[0].message.content


# =====================================
# Unified LLM Call (Gemini -> Groq -> OpenRouter)
# =====================================

def call_llm(
    messages
):

    try:

        logger.info("Trying Gemini")

        return call_gemini(messages)

    except Exception as e:

        logger.warning(e)

    try:

        logger.info("Trying Groq")

        return call_groq(messages)

    except Exception as e:

        logger.warning(e)

    logger.info("Trying OpenRouter")

    response = call_openrouter(messages)

    return response.choices[0].message.content


# =====================================
# Centralized OpenRouter Call (with fallback + retry)
# =====================================

def call_openrouter(messages, stream=False):

    logger.info("=" * 60)

    logger.info("Trying OpenRouter Models")

    logger.info("=" * 60)

    last_error = None

    for model in MODELS:

        for attempt in range(3):

            try:

                logger.info(f"Trying {model} (Attempt {attempt + 1})")

                logger.info(f"Current model : {model}")

                start = time.time()

                response = openrouter_client.chat.completions.create(

                    model=model,

                    messages=messages,

                    stream=stream,
                    temperature=0.2,

                )

                logger.info(
                    f"Response Time : {time.time()-start:.2f} seconds"
                    )

                logger.info("=" * 60)
                logger.info(f"Using model : {model}")
                logger.info("=" * 60)

                return response

            except RateLimitError as e:

                last_error = e

                logger.warning(
                    f"{model} is rate limited. Waiting 30 seconds..."
                )

                time.sleep(30)

                continue

            except NotFoundError as e:

                last_error = e

                logger.warning(f"{model} unavailable.")

                break

            except APIConnectionError as e:

                last_error = e

                logger.warning(f"{model} connection failed.")

                time.sleep(5)
                continue

            except Exception as e:

                last_error = e

                logger.warning(f"{model} failed: {e}")

                continue

    if last_error:
        raise last_error

    raise Exception("All OpenRouter models failed.")

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

        logger.info("Loading Embedding Model...")

        embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

    return embedding_model

# =====================================
# Similarity Threshold
# =====================================

SIMILARITY_THRESHOLD = 1.20


# =====================================
# Hybrid Retrieval Function
# =====================================

def retrieve_relevant_chunks(

    question,

    selected_pdf,

    user_id,

    top_k=5,

    max_chunks=5
):

    # =================================
    # Check Vector Store Exists
    # =================================

    if not os.path.exists("vector_store/faiss_index.bin"):
        return [], []

    # =================================
    # Load FAISS Index
    # =================================

    index = faiss.read_index(

        "vector_store/faiss_index.bin"
    )

    # =================================
    # Check Metadata Exists
    # =================================

    if not os.path.exists("vector_store/metadata.json"):
        return [], []

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
    # Don't search more vectors than exist
    # =================================

    top_k = min(
        max(top_k * 3, 10),
        len(pdf_chunks)
    )

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

    question_embedding = get_embedding_model().encode(

    question,

    normalize_embeddings=True

    )

    question_embedding = np.ascontiguousarray(

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

        # if distance > SIMILARITY_THRESHOLD:
        #     continue

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

        chunk_key = (

            chunk_data["page_number"],

            chunk_data["chunk_number"]
        )

        if chunk_key not in used_chunks:

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

            used_chunks.add(chunk_key)

    # =================================
    # BM25 Results
    # =================================

    for i, score in enumerate(bm25_scores):

        chunk_data = pdf_chunks[i]

        chunk_key = (

            chunk_data["page_number"],

            chunk_data["chunk_number"]
        )

        if chunk_key not in used_chunks:

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

            used_chunks.add(chunk_key)

    # =================================
    # Sort Results
    # =================================

    combined_results = sorted(
        combined_results,
        key=lambda x: (
            x["score"],
            -x["page_number"]
        ),
        reverse=True
    )

    # =================================
    # Final Chunks
    # =================================

    retrieved_chunks = []

    retrieved_sources = []

    used_chunks = set()

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

    chat_history=None
):

    if chat_history is None:
        chat_history = []

    if not question.strip():
        
        return {
            "question": "",
            "answer": "Question cannot be empty.",
            "sources": []
        }

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

    context = ""

    for chunk, source in zip(
        retrieved_chunks,
        retrieved_sources
    ):

        context += (
            f"\n[Page {source['page_number']}]\n"
        )

        context += chunk

        context += "\n-----------------------\n"

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
You are an intelligent AI PDF Assistant.

Rules:

Answer ONLY using the supplied document.

Never use outside knowledge.

Never guess.

If the answer is unavailable reply exactly:

"I could not find that information in this document."

Always be concise.

Mention page numbers whenever possible.

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

        answer = call_llm(

            [

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

    except Exception as e:

        logger.error(traceback.format_exc())

        answer = (
            "The AI service is temporarily unavailable. Please try again."
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

    if not os.path.exists("vector_store/metadata.json"):

        return {

            "summary":
            "No content found."
        }

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

    MAX_CONTEXT = 18000

    document_text = document_text[:MAX_CONTEXT]

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

        summary = call_llm(

            [

                {

                    "role": "user",

                    "content": prompt

                }

            ]

        )

    except Exception as e:

        logger.error(traceback.format_exc())

        summary = (
            "The summary service is temporarily unavailable."
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

    chat_history=None
):

    if chat_history is None:
        chat_history = []

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

    context = "\n-----------------------\n".join(
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
You are an intelligent AI PDF Assistant.

Rules:

Answer ONLY using the supplied document.

Never use outside knowledge.

Never guess.

If the answer is unavailable reply exactly:

"I could not find that information in this document."

Always be concise.

Mention page numbers whenever possible.

ACTIVE PDF:
{selected_pdf}

CHAT HISTORY:
{history_text}

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}
"""

    # NOTE: Streaming stays on OpenRouter. call_llm() (Gemini/Groq) returns
    # a plain string, not a token stream, so it can't be substituted here
    # without separate streaming implementations for each provider.

    try:

        stream = call_openrouter(

            [

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            stream=True

        )

    except Exception as e:

        logger.error(traceback.format_exc())

        yield f"\nStreaming Error: {repr(e)}"

        return

    try:

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
        logger.error(traceback.format_exc())

        yield f"\nStreaming Error: {repr(e)}"