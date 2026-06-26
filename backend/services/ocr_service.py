import pytesseract
from pdf2image import convert_from_path

# Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_with_ocr(pdf_path):

    extracted_pages = []

    # Convert PDF pages into images
    images = convert_from_path(pdf_path)

    # OCR extraction
    for index, image in enumerate(images):

        text = pytesseract.image_to_string(image)

        if not text:
            text = "[OCR COULD NOT DETECT TEXT]"

        extracted_pages.append({
            "page_number": index + 1,
            "character_count": len(text),
            "text": text
        })

    return extracted_pages