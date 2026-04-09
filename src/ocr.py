#OCR (optical character recognition module)

import base64
import io
import time
from pathlib import Path
from mistralai.client import Mistral
from pypdf import PdfReader, PdfWriter
from logger import get_logger

log = get_logger(__name__)

_MAX_PAGES = 3  # first X pages cover MD&A and key financials in most filings
_RETRIES = 3
_RETRY_DELAY = 5  # seconds between retries on 503


def pdf_to_text(client: Mistral, pdf_path: Path) -> str:
    log.info(f"OCR: {pdf_path.name} ({pdf_path.stat().st_size / 1_000_000:.1f} MB)")
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    pages_to_process = min(total, _MAX_PAGES)

    # Trim to first N pages so the base64 payload stays within Mistral's limit
    writer = PdfWriter()
    for i in range(pages_to_process):
        writer.add_page(reader.pages[i])
    buf = io.BytesIO()
    writer.write(buf)
    b64 = base64.standard_b64encode(buf.getvalue()).decode()
    doc = {"type": "document_url", "document_url": f"data:application/pdf;base64,{b64}"}

    log.info(f"Sending pages 1–{pages_to_process} of {total} to Mistral OCR")
    for attempt in range(1, _RETRIES + 1):
        try:
            resp = client.ocr.process(model="mistral-ocr-latest", document=doc)
            # Each page comes back as markdown, tables and headers are preserved
            text = "\n\n".join(page.markdown for page in resp.pages)
            log.info(f"Extracted {len(text):,} chars across {pages_to_process} pages")
            return text
        except Exception as exc:
            if attempt < _RETRIES:
                log.warning(f"OCR attempt {attempt} failed ({exc}) — retrying in {_RETRY_DELAY}s")
                time.sleep(_RETRY_DELAY)
            else:
                raise
