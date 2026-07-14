import io
import os
import tempfile
import docx
from pdfminer.high_level import extract_text


def extract_text_from_file(content: bytes, filename: str) -> str:
    """
    SAFE, synchronous text extraction.
    NO async
    NO BytesIO misuse
    NO OCR here (handled elsewhere)
    """

    filename = filename.lower()

    # --------------------
    # DOCX
    # --------------------
    if filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    # --------------------
    # PDF (TEXT PDFs ONLY)
    # --------------------
    if filename.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            text = extract_text(tmp_path)
            return text or ""
        finally:
            os.remove(tmp_path)

    # --------------------
    # TXT / MD
    # --------------------
    if filename.endswith((".txt", ".md")):
        return content.decode("utf-8", errors="ignore")

    # --------------------
    # FALLBACK
    # --------------------
    return content.decode("utf-8", errors="ignore")
