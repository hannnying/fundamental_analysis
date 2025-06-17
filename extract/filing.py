from db_uri import engine
import os
import yfinance as yf
from sqlalchemy import create_engine, Table, Column, MetaData, String, Text, Integer
from utils import download_json_filings, get_cik_from_url, cik_to_ticker, ticker_to_cik

class FilingDataLoader:
    def __init__(self):
        self.engine = engine
        self.metadata = MetaData()
        self.filing_table = self._define_table()
        self._create_table()

    def _define_table(self):
        return Table(
            "Filing",
            self.metadata,
            Column("url", Text, primary_key=True),
            Column("ticker", String),
            Column("cik", String),
            Column("form_type", String), # planning for all to be 10-K
            Column("fiscal_year", Integer),
            Column("quarter", Integer), # Optional, if 10-Q
            Column("local_path", Text)
        )

    def _create_table(self):
        self.metadata.create_all(self.engine)

    def create_filings(self, url, fiscal_year, form_type):
        cik = get_cik_from_url(url)
        ticker = cik_to_ticker(cik)
        return {
            "url": url,
            "ticker": ticker,
            "cik": cik,
            "fiscal_year": fiscal_year,
            "form_type": form_type,
        }

    def load_filings(self, filings, extract=False):
        """
        filings: List of dicts with keys:
        ticker, cik, url, fiscal_year, form_type, local_path (optional).
        extract: Boolean: True means to extract if it has not been extracted
        """
        for filing in filings:
            if "local_path" not in filing:
                filing["local_path"] = download_json_filings(filing, False)
            
        with self.engine.begin() as conn:
            conn.execute(
                self.filing_table.insert().prefix_with("OR REPLACE"),
                filings
            )
 

if __name__ == "__main__":
    filings_loader = FilingDataLoader()
    # filing info only exists if its meant to be fetched from sec API, (should we integrate with yfinance data? or should that only be in income_statement etc.)
    inputs = [
        ["https://www.sec.gov/Archives/edgar/data/789019/000156459017014900/msft-10k_20170630.htm", 2017, "10-K"],
        ["https://www.sec.gov/Archives/edgar/data/789019/000156459018019062/msft-10k_20180630.htm", 2018, "10-K"],
        ["https://www.sec.gov/Archives/edgar/data/789019/000156459019027952/msft-10k_20190630.htm", 2019, "10-K"],
        ["https://www.sec.gov/Archives/edgar/data/789019/000156459020034944/msft-10k_20200630.htm", 2020, "10-K"],
        ["https://www.sec.gov/Archives/edgar/data/320193/000032019318000145/a10-k20189292018.htm", 2018, "10-K"]
    ]
    
    filings = []

    for url, fiscal_year, form_type in inputs:
        filings.append(filings_loader.create_filings(url, fiscal_year, form_type))

    filings_loader.load_filings(filings)

