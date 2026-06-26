from sentence_transformers import (
    SentenceTransformer
)

# =====================================
# Load Embedding Model
# =====================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =====================================
# Generate Embeddings
# =====================================

def generate_embeddings(

    chunks,

    user_id
):

    embedded_chunks = []

    # =================================
    # Process Chunks
    # =================================

    for chunk in chunks:

        text = chunk["text"]

        # =================================
        # Generate Embedding
        # =================================

        embedding = model.encode(text)

        # =================================
        # Store Full Metadata
        # =================================

        embedded_chunks.append({

            "user_id":
            user_id,

            "pdf_file":
            chunk["pdf_file"],

            "page_number":
            chunk["page_number"],

            "chunk_number":
            chunk["chunk_number"],

            "chunk_length":
            chunk["chunk_length"],

            "text":
            text,

            "embedding":
            embedding.tolist()
        })

    # =================================
    # Save Embedding Debug File
    # =================================

    with open(

        "embedding_output.txt",

        "w",

        encoding="utf-8"

    ) as f:

        for item in embedded_chunks:

            f.write(
                "\n\n========================\n"
            )

            f.write(
                f"USER ID : "
                f"{item['user_id']}\n"
            )

            f.write(
                f"PDF FILE : "
                f"{item['pdf_file']}\n"
            )

            f.write(
                f"PAGE NUMBER : "
                f"{item['page_number']}\n"
            )

            f.write(
                f"CHUNK NUMBER : "
                f"{item['chunk_number']}\n"
            )

            f.write(
                f"TEXT:\n"
                f"{item['text'][:300]}\n\n"
            )

            f.write(
                "EMBEDDING VECTOR "
                "(FIRST 20 VALUES):\n"
            )

            f.write(
                str(item["embedding"][:20])
            )

            f.write("\n")

    print(

        f"\nTotal Embeddings Generated: "
        f"{len(embedded_chunks)}"
    )

    return embedded_chunks