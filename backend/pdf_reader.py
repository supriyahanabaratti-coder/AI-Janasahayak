
import pymupdf
import easyocr
import numpy as np
from PIL import Image
import io

# Initialize OCR reader
reader = easyocr.Reader(['en'], gpu=False)


def extract_text_from_pdf(uploaded_file):
    pdf_document = pymupdf.open(
        stream=uploaded_file.getvalue(),
        filetype="pdf"
    )

    extracted_pages = []

    for page_number, page in enumerate(pdf_document):

        # First, try normal PDF text extraction
        text = page.get_text().strip()

        # If no readable text, use OCR
        if len(text) < 20:
            pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
            image = Image.open(
                io.BytesIO(pix.tobytes("png"))
            ).convert("RGB")

            image_array = np.array(image)
            ocr_results = reader.readtext(image_array)

            text = "\n".join(
                result[1] for result in ocr_results
            )

        extracted_pages.append({
            "page": page_number + 1,
            "text": text
        })

    pdf_document.close()

    return extracted_pages
