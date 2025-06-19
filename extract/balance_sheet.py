from db_uri import engine
import json
from pathlib import Path
from sqlalchemy import Table, Column, String, Float, MetaData, Integer
from utils import fetch_financial_statement_yf, json_to_table
import yfinance as yf

class BalanceSheetLoader:
    def __init__(self):
        self.engine = engine
        self.metadata = MetaData()
        self.income_statement_table = self._define_table()
        self.columns = ["current_assets", "total_assets", "current_liabilities", "total_liabilities", "stockholders_equity", "net_inventory", "net_accounts_receivables"]
        self.standard_mappings = {
            "AssetsCurrent": "current_assets",
            "CurrentAssets": "current_assets",
            "Assets": "total_assets",
            "TotalAssets": "total_assets",
            "LiabilitiesCurrent": "current_liabilities",
            "CurrentLiabilities": "current_liabilities",
            "Liabilities": "total_liabilities",
            "TotalLiabilitiesNetMinorityInterest": "total_liabilities",
            "InventoryNet": "net_inventory",
            "Inventory": "net_inventory",
            "StockholdersEquity": "stockholders_equity",
            "AccountsReceivableNetCurrent": "net_accounts_receivables",
            "AccountsReceivable": "net_accounts_receivables"
        }
        self._create_table()


    def _define_table(self):
        return Table(
            "BalanceSheet",
            self.metadata,
            Column("ticker", String, primary_key=True),
            Column("fiscal_year", Integer, primary_key=True),
            Column("source", String),
            Column("current_assets", Float),
            Column("total_assets", Float),
            Column("current_liabilities", Float),
            Column("total_liabilities", Float),
            Column("stockholders_equity", Float),
            Column("net_inventory", Float),
            Column("net_accounts_receivables", Float)
        )

    def _create_table(self):
        self.metadata.create_all(self.engine)


    def load_balance_sheet_by_json(self, tickers_fiscal_years):
        """
        tickers_fiscal_years: list of lists, where each element is [ticker, fiscal_year]
        """
        balance_sheets = []
        for ticker, fiscal_year in tickers_fiscal_years:
            try:
                filing_income_statements = json_to_table(ticker, "balance", fiscal_year, self.standard_mappings, self.columns)
                balance_sheets.extend(filing_income_statements)
            except Exception as e:
                print(f"Error fetching income statements of {ticker}: {e}")

        if balance_sheets:
            with self.engine.begin() as conn:
                conn.execute(
                    self.income_statement_table.insert().prefix_with("OR REPLACE"),
                    balance_sheets
                )


    def load_balance_sheet_by_yf_tickers(self, tickers):
        balance_sheets = []
        for ticker in tickers:
            try:
                balance_sheet_2124 = fetch_financial_statement_yf(ticker, "balance", self.standard_mappings, self.columns)
                print(f"Fetched 2021-2024 balance sheerts of {ticker}")
                balance_sheets.extend(balance_sheet_2124)
            except Exception as e:
                print(f"Error fetching balance sheets of {ticker}: {e}")
        
        if balance_sheets:
            with self.engine.begin() as conn:
                conn.execute(
                    self.income_statement_table.insert().prefix_with("OR REPLACE"),
                    balance_sheets
                )

if __name__ == "__main__":
    loader = BalanceSheetLoader()
    tickers = ["MSFT", "AAPL"]
    loader.load_balance_sheet_by_yf_tickers(tickers)    
    loader.load_balance_sheet_by_json([["MSFT", 2018], ["AAPL", 2018], ["AAPL", 2019]])