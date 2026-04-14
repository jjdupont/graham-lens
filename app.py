import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from mistralai.client import Mistral

from src.pipeline import run
from src.compare import load_signals
from logger import setup_logging, get_logger

load_dotenv()
setup_logging()
log = get_logger(__name__)

st.set_page_config(page_title="GrahamLens", page_icon="📊", layout="wide")
st.title("GrahamLens: Value Screener")
st.caption("Mistral OCR + structured extraction:  Graham scorecard dataset")

api_key = os.getenv("MISTRAL_API_KEY") or st.sidebar.text_input("Mistral API Key", type="password")
client = Mistral(api_key=api_key) if api_key else None

st.header("Upload Annual Reports")
uploaded = st.file_uploader("PDF filings", type="pdf", accept_multiple_files=True)

if st.button("Run Analysis", disabled=not (uploaded and client)):
    bar = st.progress(0)
    for i, file in enumerate(uploaded):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = Path(tmp.name)
        with st.spinner(f"Processing {file.name}…"):
            try:
                sc = run(tmp_path, client)
                st.success(f"{sc.company} ({sc.year}) — Score: {sc.graham_score_llm}/100")
            except Exception as exc:
                st.error(f"{file.name}: {exc}")
        bar.progress((i + 1) / len(uploaded))

st.header("Screener Results")
df = load_signals()

if df.empty:
    st.info("No companies analysed yet. Upload PDFs above.")
else:
    st.dataframe(
        df.style.background_gradient(subset=["graham_score_llm"], cmap="RdYlGn"),
        use_container_width=True,
    )

    selected = st.selectbox("View full scorecard:", df["company"].tolist())
    if selected:
        row = df[df["company"] == selected].iloc[0]
        c1, c2 = st.columns(2)
        c1.metric("Graham Score", f"{row['graham_score_llm']}/100")
        c2.metric("Confidence", f"{row['confidence']:.0%}")
        st.write(f"**Moat signals:** {row['moat_signals']}")
        st.write(f"**Red flags:** {row['red_flags']}")
        st.write(f"**Leverage:** {row['leverage']} | **Liquidity:** {row['liquidity']} | **Earnings:** {row['stability']}, {row['trend']}")
