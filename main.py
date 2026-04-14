import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from mistralai.client import Mistral

from src.pipeline import run, run_all
from src.compare import load_signals, print_ranking
from logger import setup_logging

load_dotenv()
setup_logging()


def main():
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    run = True

    # If a PDF path is passed as argument, process just that file
    if run == True:
        if len(sys.argv) > 1:
            pdf = Path(sys.argv[1])
            run(pdf, client)
        else:
            run_all(client=client)

    df = load_signals()
    print_ranking(df)


if __name__ == "__main__":
    main()
