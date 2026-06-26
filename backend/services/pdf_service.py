import fitz

from services.ocr_service import (
    extract_text_with_ocr
)


# =====================================
# Extract Text From PDF
# =====================================

def extract_text_from_pdf(

    pdf_path
):

    extracted_pages = []

    # =================================
    # Open PDF
    # =================================

    doc = fitz.open(pdf_path)

    # =================================
    # Extract Page Text
    # =================================

    for page_number in range(len(doc)):

        page = doc.load_page(
            page_number
        )

        text = page.get_text().strip()

        # =============================
        # Handle Empty Pages
        # =============================

        if not text:

            text = (
                "[NO TEXT FOUND]"
            )

        extracted_pages.append({

            "page_number":
            page_number + 1,

            "character_count":
            len(text),

            "text":
            text
        })

    # =================================
    # Combine Text
    # =================================

    combined_text = " ".join(

        [
            page["text"]

            for page in extracted_pages
        ]
    )

    # =================================
    # OCR Fallback
    # =================================

    if len(combined_text.strip()) < 50:

        print(
            "\nUsing OCR Extraction..."
        )

        extracted_pages = (

            extract_text_with_ocr(
                pdf_path
            )
        )

    # =================================
    # Save Debug Output
    # =================================

    with open(

        "extracted_output.txt",

        "w",

        encoding="utf-8"

    ) as f:

        for page_data in extracted_pages:

            f.write(

                "\n\n========================\n"
            )

            f.write(

                f"PAGE NUMBER: "
                f"{page_data['page_number']}\n"
            )

            f.write(

                f"CHARACTER COUNT: "
                f"{page_data['character_count']}\n"
            )

            f.write(

                "========================\n\n"
            )

            f.write(
                page_data["text"]
            )

            f.write("\n\n")

    print(

        f"\nTotal Pages Extracted: "
        f"{len(extracted_pages)}"
    )

    return extracted_pages