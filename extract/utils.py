import json
import os
from pathlib import Path
import pandas as pd
from sec_api import XbrlApi
from sec_cik_mapper import StockMapper
from urllib.parse import urlparse
import warnings
import yfinance as yf

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
    """Downloads or retrieves cached SEC filing XBRL data in JSON format.

    Handles both fetching fresh filings from the SEC API and retrieving previously
    cached filings. Files are stored in a structured cache directory with standardized
    filenames.

    Args:
        filing (dict): A dictionary containing filing metadata with keys:
            - ticker (str): Company stock ticker symbol
            - fiscal_year (int/str): Fiscal year of the filing
            - form_type (str): SEC form type (e.g., '10-K', '10-Q')
            - url (str): URL to the SEC filing document
        extract (bool): If True, downloads fresh filing when not in cache.
                       If False, only checks cache.

    Returns:
        str or None: Relative path to the JSON file if successful (from project root),
                     None if file doesn't exist and extract=False.
    """
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


def load_json_financial_statement(xbrl_json, statement_type, standard_mapping, columns):
    """
    Extracts a standardized financial statement from XBRL JSON data.

    Args:
        xbrl_json : dict
            The SEC filing JSON containing financial statement data.
        statement_type : str
            One of "income", "balance", or "cash_flow".
        standard_mapping : dict
            A mapping from US GAAP item names to standardized column names.
        columns : list of str
            The list of standardized column names to extract.

    Returns:
        pandas.DataFrame
            A DataFrame indexed by fiscal year with selected standardized columns.
    """
    financial_statement_store = {}
    financial_statement_map = {"income": "StatementsOfIncome",
                               "balance": "BalanceSheets",
                               "cash_flow": "StatementsOfCashFlows"}

    for usGaapItem in xbrl_json[financial_statement_map[statement_type]]:
        col_name = standard_mapping.get(usGaapItem, usGaapItem)
        values = []
        indicies = set()
        if col_name not in columns:
            continue

        for fact in xbrl_json[financial_statement_map[statement_type]][usGaapItem]:
            # only consider items without segment. not required for our analysis.
            if 'segment' not in fact:
                try:
                    index = pd.to_datetime(fact['period']['endDate']).year
                except KeyError:
                    index = pd.to_datetime(fact['period']['instant']).year
                # ensure no index duplicates are created
                if index not in indicies:
                    values.append(fact['value'])
                    indicies.add(index)                    

        financial_statement_store[col_name] = pd.Series(values, index=indicies) 

    financial_statement = pd.DataFrame(financial_statement_store)
    return financial_statement


def load_filing_json(ticker, fiscal_year, form_type="10-K"):
    """
    Loads a locally cached SEC filing JSON for a given company.

    Args:
        ticker : str
            The stock ticker symbol of the company (e.g., "AAPL").
        fiscal_year : int or str
            The fiscal year of the filing to load (e.g., 2023).
        form_type : str, optional
            The type of SEC form to load (default is "10-K").

    Returns:
    dict or None
        The parsed JSON content of the filing if the file exists, otherwise None.
    """
    BASE_DIR = Path(__file__).resolve().parent.parent  # This gives you 'project/'
    cache_folder = BASE_DIR / "data" / "sec_filings"
    filename = f"{ticker}_{fiscal_year}_{form_type}.json"
    filepath = cache_folder / filename

    if filepath.exists():
        with open(filepath, "r") as f:
            xbrl_json = json.load(f)
            return xbrl_json
    else:
        print(f"{filepath} does not exist.")
        return None
    

def json_to_table(ticker, statement_type, fiscal_year, standard_mappings, columns):
    """
    Converts SEC filing JSON data into a list of standardized financial records.

    Args:
        ticker : str
            The stock ticker symbol of the company (e.g., "AAPL").
        statement_type : str
            One of "income", "balance", or "cash_flow".
        fiscal_year : int or str
            The fiscal year of the SEC filing to process.
        standard_mappings : dict
            A dictionary that maps US GAAP item names (from the filing) to standardized column names.
        columns : list of str
            The list of standardized column names to extract from the financial statement.

    Returns:
        list of dict
            A list of dictionaries where each dictionary represents one year's financial data,
            with keys: the specified columns, 'fiscal_year', 'ticker', and 'source'.
            If a column is missing in the data, its value is set to False.
    """
    xbrl_json = load_filing_json(ticker, fiscal_year)
    financial_statements = load_json_financial_statement(xbrl_json, statement_type, standard_mappings, columns)
    records = []

    for year in financial_statements.index:
        d = {}
        for column in columns:
            try:
                d[column] = float(financial_statements.loc[year, column])
            except Exception as e:
                print(f"{e} not in filing")
                d[column] = False
            d['fiscal_year'] = year
            d['ticker'] = ticker
            d['source'] = "sec_filings_json"
            records.append(d)
    return records


def fetch_financial_statement_yf(ticker, statement_type, standard_mappings, columns):
    if statement_type == "income":
        financial_statement_2124 = yf.Ticker(ticker).get_income_stmt().T
    elif statement_type == "balance":
        financial_statement_2124 = yf.Ticker(ticker).get_balance_sheet().T
    elif statement_type == "cash_flow":
        financial_statement_2124 = yf.Ticker(ticker).get_cash_flow().T

    records = []
    for dt in financial_statement_2124.index:
        d = {}
        for col in financial_statement_2124.columns:
            col_name = standard_mappings.get(col, col)
            if col_name not in columns:
                continue
            
            d[col_name] = financial_statement_2124.loc[dt, col]
        d["ticker"] = ticker
        d["fiscal_year"] = dt.year
        d["source"] = "yfinance"
        records.append(d)
    return records