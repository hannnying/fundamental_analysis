from db_uri import engine
from financials import FinancialsLoader
import json
from pathlib import Path
from sqlalchemy import Table, Column, String, Float, MetaData, Integer
from utils import fetch_financial_statement_yf, json_to_table
import yfinance as yf

class IncomeStatementLoader(FinancialsLoader):
    def __init__(self):
        super().__init__("IncomeStatement")


    @property
    def standard_mappings(self):
        return {
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
    
    
    @property
    def columns(self):
        return ["revenue", "cost_of_revenue", "net_income", "operating_income", "gross_profit"]


    def define_table(self):
        table = super().define_table()
        for col in self.columns:
            table.append_column(Column(col, Float))
        return table
    

if __name__ == "__main__":
    loader = IncomeStatementLoader()
    # tickers = ["MSFT", "AAPL"]
    # loader.load_income_statement_by_yf_tickers(tickers)    
    loader.load_income_statement_by_json([["MSFT", 2018], ["AAPL", 2018], ["AAPL", 2019]])