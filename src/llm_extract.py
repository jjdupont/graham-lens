import json
import time
from mistralai.client import Mistral
from src.schema import GrahamScorecard
from logger import get_logger

log = get_logger(__name__)

_MAX_CHARS = 6000  # Keep first X chars - covers the MD&A and key financials in most filings

# Derive the schema description directly from the Pydantic model so the prompt never drifts out of sync with schema.py
_SCHEMA_JSON = json.dumps(GrahamScorecard.model_json_schema(), indent=4)

_SYSTEM = f"""You are a value investing analyst trained on Benjamin Graham's principles (The Intelligent Investor).
Given text from a company's financial filing, extract a Graham scorecard as JSON.
Return ONLY valid JSON matching this schema:

{_SCHEMA_JSON}

graham_score_llm rubric: 0 = deeply distressed, 50 = average, 100 = textbook Graham stock
(low P/E, minimal debt, 10+ years of stable earnings, margin of safety).
confidence: how much of the filing text was sufficient to judge each dimension reliably."""


_RETRIES = 4


def extract_scorecard(client: Mistral, text: str, model: str = "mistral-small-latest") -> GrahamScorecard:
    log.info("Extracting Graham scorecard: work in progress...")
    chunk = text[:_MAX_CHARS]
    messages = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": f"Extract the Graham scorecard from this filing text:\n\n{chunk}"},
    ]
    for attempt in range(1, _RETRIES + 1):
        try:
            resp = client.chat.complete(
                model=model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            break
        except Exception as exc:
            if attempt < _RETRIES:
                # 429 rate limits need a longer wait than transient 503s
                delay = 30 if "429" in str(exc) else 5
                log.warning(f"LLM attempt {attempt} failed ({exc}) — retrying in {delay}s")
                time.sleep(delay)
            else:
                raise
    data = json.loads(resp.choices[0].message.content)
    scorecard = GrahamScorecard(**data)
    log.info(f"Done: {scorecard.company} {scorecard.year} — score={scorecard.graham_score_llm}, conf={scorecard.confidence}")
    return scorecard
