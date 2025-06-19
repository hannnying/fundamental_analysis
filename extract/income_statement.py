from db_uri import engine
import json
from pathlib import Path
from sqlalchemy import Table, Column, String, Float, MetaData, Integer
from utils import fetch_financial_statement_yf, json_to_table
import yfinance as yf

class IncomeStatementLoader:
    def __init__(self):
        self.engine = engine
        self.metadata = MetaData()
        self.income_statement_table = self._define_table()
        self.columns = ["revenue", "cost_of_revenue", "net_income", "operating_income", "gross_profit"]
        self.standard_mappings = {
            "RevenueFromContractWithCustomerExcludingAssessedTax": "revenue",
            "Revenues": "revenue",
            "SalesRevenueNet": "revenue",
            "TotalRevenue": "revenue", #yf
            "CostOfRevenue": "cost_of_revenue",
            "CostOfGoodsAndServicesSold": "cost_of_revenue",
            "OperatingIncome": "operating_income", # yf
            "OperatingIncomeLoss": "operating_income",
            "NetIncome": "net_income", # yf
            "NetIncomeLoss": "net_income",
            "GrossProfit": "gross_profit" # may not always be available
        }
        self._create_table()


    def _define_table(self):
        return Table(
            "IncomeStatement",
            self.metadata,
            Column("ticker", String, primary_key=True),
            Column("fiscal_year", Integer, primary_key=True),
            Column("source", String),
            Column("revenue", Float),
            Column("cost_of_revenue", Float),
            Column("gross_profit", Float),
            Column("operating_income", Float),
            Column("net_income", Float)
        )

    def _create_table(self):
        self.metadata.create_all(self.engine)


    def load_income_statement_by_json(self, tickers_fiscal_years):
        """
        tickers_fiscal_years: list of lists, where each element is [ticker, fiscal_year]
        """
        income_statements = []
        for ticker, fiscal_year in tickers_fiscal_years:
            try:
                filing_income_statements = json_to_table(ticker, "income", fiscal_year, self.standard_mappings, self.columns)
                income_statements.extend(filing_income_statements)
            except Exception as e:
                print(f"Error fetching income statements of {ticker}: {e}")

        if income_statements:
            with self.engine.begin() as conn:
                conn.execute(
                    self.income_statement_table.insert().prefix_with("OR REPLACE"),
                    income_statements
                )


    def load_income_statement_by_yf_tickers(self, tickers):
        income_statements = []
        for ticker in tickers:
            try:
                income_stmt_2124 = fetch_financial_statement_yf(ticker, "income", self.standard_mappings, self.columns)
                print(f"Fetched 2021-2024 income statements of {ticker}")
                income_statements.extend(income_stmt_2124)
            except Exception as e:
                print(f"Error fetching income statements of {ticker}: {e}")
        
        if income_statements:
            with self.engine.begin() as conn:
                conn.execute(
                    self.income_statement_table.insert().prefix_with("OR REPLACE"),
                    income_statements
                )

if __name__ == "__main__":
    loader = IncomeStatementLoader()
    # tickers = ["MSFT", "AAPL"]
    # loader.load_income_statement_by_yf_tickers(tickers)    
    loader.load_income_statement_by_json([["MSFT", 2018], ["AAPL", 2018], ["AAPL", 2019]])