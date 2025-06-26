from sqlalchemy import Column, Float, Integer, String, Boolean
from internal.database import Base, engine

class Company(Base):
    __tablename__ = "companies"

    ticker=Column(String, primary_key=True)
    cik=Column(String)
    name=Column(String)
    sector=Column(String) 
    industry=Column(String)


class IncomeStatement(Base):
    __tablename__ = "income_statements"

    ticker=Column(String, primary_key=True)
    fiscal_year=Column(Integer, primary_key=True)
    revenue=Column(Float, default=None)
    cost_of_revenue=Column(Float, default=None)
    net_income=Column(Float, default=None)
    operating_income=Column(Float, default=None)
    gross_profit=Column(Float, default=None)
    basic_eps=Column(Float, default=None)


class BalanceSheet(Base):
    __tablename__ = "balance_sheets"

    ticker=Column(String, primary_key=True)
    fiscal_year=Column(Integer, primary_key=True)
    cash_equivalents=Column(Float, default=None)
    current_assets=Column(Float, default=None)
    total_assets=Column(Float, default=None)
    current_liabilities=Column(Float, default=None)
    total_liabilites=Column(Float, default=None)
    stockholders_equity=Column(Float, default=None)
    net_inventory=Column(Float, default=None)
    net_accounts_receivables=Column(Float, default=None)

    

Base.metadata.create_all(engine)