from db_uri import engine
import json
from pathlib import Path
from sqlalchemy import Table, Column, String, Float, MetaData, Integer
from utils import fetch_financial_statement_yf, json_to_table
import yfinance as yf

class FinancialsLoader:
    def __init__(self, statement_type):
        self.engine = engine
        self.metadata = MetaData() # should this be in db_uri like engine
        self.statement_type = statement_type
        self.table = self.define_table()
        self._create_table()


    @property
    def standard_mappings(self):
        """To be implemented by child classes"""
        raise NotImplementedError
        
    @property
    def columns(self):
        """To be implemented by child classes"""
        raise NotImplementedError
    

    def _create_table(self):
        self.metadata.create_all(self.engine)


    def define_table(self):
        return Table(
            f"{self.statement_type}",
            self.metadata,
            Column("ticker", String, primary_key=True),
            Column("fiscal_year", Integer, primary_key=True),
            Column("source", String),
        )
    

    def load_financials_by_json(self, tickers_fiscal_years):
        """
        tickers_fiscal_years: list of lists, where each element is [ticker, fiscal_year]
        """
        statements = []
        for ticker, fiscal_year in tickers_fiscal_years:
            try:
                filing_financial_statements = json_to_table(ticker, self.statement_type, fiscal_year, self.standard_mappings, self.columns)
                statements.extend(filing_financial_statements)
            except Exception as e:
                print(f"Error fetching {self.statement_type} statements of {ticker}: {e}")

        if statements:
            with self.engine.begin() as conn:
                conn.execute(
                    self.table.insert().prefix_with("OR REPLACE"),
                    statements
                )


    def load_financials_by_yf_tickers(self, tickers):
        statements = []
        for ticker in tickers:
            try:
                statement_2124 = fetch_financial_statement_yf(ticker, self.statement_type, self.standard_mappings, self.columns)
                print(f"Fetched 2021-2024 {self.statement_type} of {ticker}")
                statements.extend(statement_2124)
            except Exception as e:
                print(f"Error fetching {self.statement_type} of {ticker}: {e}")

        if statements:
            with self.engine.begin() as conn:
                conn.execute(
                    self.table.insert().prefix_with("OR REPLACE"),
                    statements
                )