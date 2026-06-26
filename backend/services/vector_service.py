import faiss
import numpy as np
import json
import os


# =====================================
# Create / Update Vector Store
# =====================================

def create_vector_store(
    embedded_chunks
):

    new_vectors = []
    new_metadata = []

    # =================================
    # Process Embedded Chunks
    # =================================

    for item in embedded_chunks:

        new_vectors.append(
            item["embedding"]
        )

        # ONLY CHANGE:
        # Added user_id
        new_metadata.append({

            "user_id":
            item["user_id"],

            "pdf_file":
            item["pdf_file"],

            "page_number":
            item["page_number"],

            "chunk_number":
            item["chunk_number"],

            "text":
            item["text"]
        })

    # =================================
    # Convert To NumPy
    # =================================

    new_vectors = np.array(
        new_vectors
    ).astype("float32")

    # =================================
    # Create vector_store Folder
    # =================================

    os.makedirs(
        "vector_store",
        exist_ok=True
    )

    faiss_path = (
        "vector_store/faiss_index.bin"
    )

    metadata_path = (
        "vector_store/metadata.json"
    )

    # =================================
    # Existing Vector Store
    # =================================

    if (
        os.path.exists(faiss_path)
        and
        os.path.exists(metadata_path)
    ):

        print(
            "\nExisting Vector Store Found"
        )

        index = faiss.read_index(
            faiss_path
        )

        index.add(
            new_vectors
        )

        with open(
            metadata_path,
            "r",
            encoding="utf-8"
        ) as f:

            old_metadata = json.load(f)

        combined_metadata = (
            old_metadata
            +
            new_metadata
        )

    else:

        print(
            "\nCreating New Vector Store"
        )

        dimension = (
            new_vectors.shape[1]
        )

        index = faiss.IndexFlatL2(
            dimension
        )

        index.add(
            new_vectors
        )

        combined_metadata = (
            new_metadata
        )

    # =================================
    # Save Index
    # =================================

    faiss.write_index(
        index,
        faiss_path
    )

    # =================================
    # Save Metadata
    # =================================

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            combined_metadata,
            f,
            ensure_ascii=False,
            indent=4
        )

    # =================================
    # Logs
    # =================================

    print(
        "\nFAISS Vector Store Updated"
    )

    print(
        f"Total Stored Vectors: "
        f"{index.ntotal}"
    )

    print(
        f"Total Metadata Entries: "
        f"{len(combined_metadata)}"
    )

    # =================================
    # Return Response
    # =================================

    return {

        "status":
        "success",

        "total_vectors":
        index.ntotal,

        "total_documents":
        len(
            set(
                item["pdf_file"]
                for item in combined_metadata
            )
        )
    }