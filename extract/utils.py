import json
import os
from pathlib import Path
import pandas as pd
from sec_api import XbrlApi
from sec_cik_mapper import StockMapper
from urllib.parse import urlparse
import warnings

warnings.filterwarnings('ignore')
API_KEY = '63ac8713495d5f0bd94ce8c8c27b6f1710d001d6737156612267f96716bb27db'
mapper = StockMapper()

def cik_to_ticker(cik):
    return list(mapper.cik_to_tickers[cik])[0]


def ticker_to_cik(ticker):
    return mapper.ticker_to_cik[ticker]

def get_cik_from_url(url):
    path_parts = urlparse(url).path.split('/')
    # The CIK is the 4th part after splitting by '/'
    # Example path: /Archives/edgar/data/1326801/000132680125000017/meta-12312024x10kexhibit191.htm
    try:
        cik = path_parts[4]
        leading_zeros = 10 - len(cik)
        return "0" * leading_zeros + cik
    except IndexError:
        return None


def download_json_filings(filing, extract):
    xbrl_api = XbrlApi(API_KEY)
    BASE_DIR = Path(__file__).resolve().parent.parent  # This gives you 'project/'
    cache_folder = BASE_DIR / "data" / "sec_filings"
    cache_folder.mkdir(parents=True, exist_ok=True)
    filename = f"{filing["ticker"]}_{filing["fiscal_year"]}_{filing["form_type"]}.json"
    filepath = cache_folder / filename
    relative_path = os.path.relpath(filepath, start=BASE_DIR)  # Or omit start= for cwd

    if filepath.exists():
         # Convert absolute path to relative path (relative to BASE_DIR or current working dir)
        print(f"{filepath} exists.")
        return relative_path
    
    if extract:
        # Get the full XBRL JSON from the API
        print(f"Downloading: {filing["url"]}")
        xbrl_json = xbrl_api.xbrl_to_json(htm_url=filing["url"])

        # Save the full XBRL JSON to file (NOT just the parsed statement)
        with open(filepath, "w") as f:
            json.dump(xbrl_json, f)
        print(f"Saved to {filepath}.")
        return relative_path

    else:
        print(f"{filepath} does not exist. Set `extract=True` to fetch it.")
        return None

        
def load_json_income_statement(xbrl_json, standard_mapping, columns):
    income_statement_store = {}

    for usGaapItem in xbrl_json["StatementsOfIncome"]:
        col_name = standard_mapping.get(usGaapItem, usGaapItem)
        values = []
        indicies = []
        if col_name not in columns:
            continue

        for fact in xbrl_json['StatementsOfIncome'][usGaapItem]:
            # only consider items without segment. not required for our analysis.
            if 'segment' not in fact:
                index = pd.to_datetime(fact['period']['endDate']).year
                # ensure no index duplicates are created
                if index not in indicies:
                    values.append(fact['value'])
                    indicies.append(index)                    

        income_statement_store[col_name] = pd.Series(values, index=indicies) 

    income_statement = pd.DataFrame(income_statement_store)
    return income_statement