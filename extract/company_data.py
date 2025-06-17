from db_uri import engine
from sec_cik_mapper import StockMapper
import yfinance as yf
from sqlalchemy import create_engine, Table, Column, MetaData, String
from utils import ticker_to_cik

class CompanyDataLoader:
    def __init__(self):
        self.engine = engine
        self.metadata = MetaData()
        self.company_table = self._define_table()
        self._create_table()

    def _define_table(self):
        return Table(
            "Company",
            self.metadata,
            Column("ticker", String, primary_key=True),
            Column("name", String),
            Column("sector", String),
            Column("industry", String),
            Column("cik", String)
        )

    def _create_table(self):
        self.metadata.create_all(self.engine)

    def fetch_company_info(self, ticker):
        info = yf.Ticker(ticker).info
        return {
            "ticker": ticker,
            "cik": ticker_to_cik(ticker),
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }

    def load_tickers(self, tickers):
        records = []
        for ticker in tickers:
            try:
                data = self.fetch_company_info(ticker)
                print(f"[✓] Fetched: {data}")
                records.append(data)
            except Exception as e:
                print(f"[!] Error fetching {ticker}: {e}")

        if records:
            with self.engine.begin() as conn:
                conn.execute(
                    self.company_table.insert().prefix_with("OR REPLACE"),
                    records
                )

    def load_from_file(self, filepath):
        with open(filepath, "r") as f:
            tickers = [line.strip() for line in f if line.strip()]
            self.load_tickers(tickers)

# === RUN SCRIPT STYLE ===
if __name__ == "__main__":
    loader = CompanyDataLoader()
    tickers = ["AAPL", "MSFT", "GOOGL", "META"]
    loader.load_tickers(tickers)
