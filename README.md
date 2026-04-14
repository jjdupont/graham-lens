# GrahamLens

LLM-powered value investing screener. Converts company press releases into structured Graham scorecards using Mistral's OCR and structured generation APIs.

1. **OCR**: extracts text from PDF annual reports via `mistral-ocr-latest`
2. **Extraction**: prompts `mistral-small-latest` to return a structured JSON scorecard (leverage, liquidity, earnings quality, moat signals, red flags, 0–100 score)
3. **Storage**: saves one JSON per company
4. **Comparison**: loads all outputs into a ranked table

The design goal is a data-generating system. Each run adds to the dataset, which unlocks multi-company comparison, ranking, and implement future backtesting capabilities.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env # add your MISTRAL_API_KEY
```

## Run

```bash
# CLI — processes all PDFs in data/raw_pdfs/
python main.py

# Single file
python main.py data/raw_pdfs/filing.pdf

# Streamlit UI
streamlit run app.py
```

## Extensions (planned)

- Fundamentals layer: merge LLM signals with Yahoo Finance data
- Ranking engine across 100+ stocks
- RAG with Mistral embeddings for large filings
- Backtesting: top decile vs index