import logging

from typing import List

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# =====================================
# Lazy Loading Model
# =====================================

DEBUG = False

model = None


def get_model():

    global model

    if model is None:

        logger.info("Loading Embedding Model...")

        try:

            model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2"
            )

        except Exception as e:

            logger.exception(e)

            raise

    return model


# =====================================
# Generate Embeddings
# =====================================

def generate_embeddings(
    chunks: List[dict],
    user_id: int
):

    logger.info(
        "Generating embeddings for %d chunks",
        len(chunks)
    )

    embedded_chunks = []

    # =================================
    # Batch Encode All Chunks
    # =================================

    texts = [chunk["text"] for chunk in chunks]

    embeddings = get_model().encode(texts)

    # =================================
    # Store Full Metadata
    # =================================

    for chunk, embedding in zip(chunks, embeddings):

        embedded_chunks.append({
            "user_id": user_id,
            "pdf_file": chunk["pdf_file"],
            "page_number": chunk["page_number"],
            "chunk_number": chunk["chunk_number"],
            "chunk_length": chunk["chunk_length"],
            "text": chunk["text"],
            "embedding": embedding.tolist()
        })

    # =================================
    # Save Embedding Debug File (DEBUG only)
    # =================================

    if DEBUG:

        with open(
            "embedding_output.txt",
            "w",
            encoding="utf-8"
        ) as f:

            for item in embedded_chunks:

                f.write("\n\n========================\n")
                f.write(f"USER ID : {item['user_id']}\n")
                f.write(f"PDF FILE : {item['pdf_file']}\n")
                f.write(f"PAGE NUMBER : {item['page_number']}\n")
                f.write(f"CHUNK NUMBER : {item['chunk_number']}\n")
                f.write(f"TEXT:\n{item['text'][:300]}\n\n")
                f.write("EMBEDDING VECTOR (FIRST 20 VALUES):\n")
                f.write(str(item["embedding"][:20]))
                f.write("\n")

    logger.info(
        "Generated %d embeddings",
        len(embedded_chunks)
    )

    return embedded_chunks