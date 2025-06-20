from db_uri import engine
from financials import FinancialsLoader
import json
from pathlib import Path
from sqlalchemy import Table, Column, String, Float, MetaData, Integer

class BalanceSheetLoader(FinancialsLoader):
    def __init__(self):
        super().__init__("BalanceSheet")


    @property
    def standard_mappings(self):
        return {
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
    

    @property
    def columns(self):
	    return ["current_assets", "total_assets", "current_liabilities", "total_liabilities", "stockholders_equity", "net_inventory", "net_accounts_receivables"]


    def define_table(self):
        table = super().define_table()
        for col in self.columns:
            table.append_column(Column(col, Float))
        return table


if __name__ == "__main__":
    loader = BalanceSheetLoader()
    tickers = ["MSFT", "AAPL"]
    loader.load_financials_by_yf_tickers(tickers)    
    loader.load_financials_by_json([["MSFT", 2018], ["AAPL", 2018], ["AAPL", 2019]])