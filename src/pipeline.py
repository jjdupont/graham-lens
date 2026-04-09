from pathlib import Path
from mistralai.client import Mistral
from src.ocr import pdf_to_text
from src.llm_extract import extract_scorecard
from src.schema import GrahamScorecard
from logger import get_logger

log = get_logger(__name__)

OUTPUTS_DIR = Path("outputs")


def run(pdf_path: Path, client: Mistral) -> GrahamScorecard:
    OUTPUTS_DIR.mkdir(exist_ok=True)
    text = pdf_to_text(client, pdf_path)
    scorecard = extract_scorecard(client, text)
    out = OUTPUTS_DIR / f"{scorecard.company}_{scorecard.year}.json"
    out.write_text(scorecard.model_dump_json(indent=4), encoding="utf-8")
    log.info(f"[RUN] scorecard saved: {out}")
    return scorecard


def run_all(pdfs_dir: Path = Path("data/raw_pdfs"), client: Mistral | None = None) -> list[GrahamScorecard]:
    pdfs = sorted(pdfs_dir.glob("*.pdf"))
    if not pdfs:
        log.warning(f"No PDFs found in {pdfs_dir}")
        return []
    results = []
    for pdf in pdfs:
        try:
            results.append(run(pdf, client))
        except Exception as e:
            log.error(f"Failed on {pdf.name}: {e}")
    return results
