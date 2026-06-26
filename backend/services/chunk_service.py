from langchain_text_splitters import (
    RecursiveCharacterTextSplitter
)


def create_chunks(

    extracted_pages,

    pdf_filename
):

    # Store all chunks

    all_chunks = []

    # Create text splitter

    text_splitter = RecursiveCharacterTextSplitter(

        chunk_size=500,

        chunk_overlap=100,

        length_function=len
    )

    # Process each page

    for page_data in extracted_pages:

        page_number = (
            page_data["page_number"]
        )

        text = page_data["text"]

        # Skip Empty Pages

        if not text.strip():

            continue

        # Split into chunks

        chunks = text_splitter.split_text(
            text
        )

        # Store chunks

        for chunk_index, chunk in enumerate(chunks):

            chunk_data = {

                "pdf_file":
                pdf_filename,

                "page_number":
                page_number,

                "chunk_number":
                chunk_index + 1,

                "chunk_length":
                len(chunk),

                "text":
                chunk
            }

            all_chunks.append(
                chunk_data
            )
            print(chunk_data)

    print(
        f"\nTotal Chunks Created: "
        f"{len(all_chunks)}"
    )

    return all_chunks