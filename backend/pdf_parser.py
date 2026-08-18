import fitz


def extract_text_from_pdf(uploaded_file):
    pdf_bytes = uploaded_file.read()

    pdf_document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    extracted_text = []

    for page_number, page in enumerate(pdf_document, start=1):
        text = page.get_text()

        extracted_text.append({
            "page": page_number,
            "text": text
        })

    return extracted_text