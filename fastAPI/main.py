from fastAPI.internal.database import session
from fastapi import FastAPI
from fastAPI.internal.models import Company, IncomeStatement, BalanceSheet
from fastAPI.internal.utils import ticker_to_cik
import yfinance as yf

app = FastAPI()

@app.post("/companies/create")
async def create_company(ticker:str):
        info = yf.Ticker(ticker.upper()).info
        cik = ticker_to_cik(ticker)
        name = info.get("longName")
        sector = info.get("sector")
        industry = info.get("industry")

        company = Company(
                ticker=ticker,
                cik=cik,
                name=name,
                sector=sector,
                industry=industry
        )

        existing = session.get(Company, ticker)
        if not existing:
            session.add(company)
            session.commit()
            return {"Company Added": company.name}
        else:
            return {"Company Added": "Already exists"}


@app.get("/companies")
async def get_all_companies():
        companies_query = session.query(Company)
        return companies_query.all()


@app.get("/companies/{sector}")
async def get_companies_in_sector(sector:str):
       company_query = session.query(Company).filter(Company.sector==sector)
       return company_query.all()


@app.post("/income-statements/create")
async def create_income_statement(ticker:str):
    statement_2124 = yf.Ticker(ticker.upper()).get_income_stmt().T

    for filed_date in statement_2124.index:
        fiscal_year = filed_date.year
        if not session.get(IncomeStatement, (ticker, fiscal_year)):
            statement = IncomeStatement(
                ticker=ticker,
                fiscal_year=fiscal_year,
                revenue=statement_2124.loc[filed_date, "TotalRevenue"],
                cost_of_revenue=statement_2124.loc[filed_date, "CostOfRevenue"],
                net_income=statement_2124.loc[filed_date, "NetIncome"],
                operating_income=statement_2124.loc[filed_date, "OperatingIncome"],
                gross_profit=statement_2124.loc[filed_date, "GrossProfit"],
                basic_eps=statement_2124.loc[filed_date, "BasicEPS"]
            )

            session.add(statement)
            session.commit()

    years = [d.year for d in statement_2124.index]
    return {"Income Statement Added": f"{min(years)} to {max(years)} of {ticker} added"}


@app.get("/income-statements")
async def get_all_income_statements():
        income_query = session.query(IncomeStatement)
        return income_query.all()


# should generalise for IncomeStatement and BalanceSheet
@app.post("/balance-sheets/create")
async def create_balance_sheet(ticker:str):
    statement_2124 = yf.Ticker(ticker.upper()).get_income_stmt().T

    for filed_date in statement_2124.index:
        fiscal_year = filed_date.year
        if not session.get(BalanceSheet, (ticker, fiscal_year)):
            statement = BalanceSheet(
                ticker=ticker,
                fiscal_year=fiscal_year,
                cash_equivalents=statement_2124.loc[filed_date, 'CashAndCashEquivalents'],
                current_assets=statement_2124.loc[filed_date, 'CurrentAssets'],
                total_assets=statement_2124.loc[filed_date, 'TotalAssets'],
                current_liabilities=statement_2124.loc[filed_date, 'CurrentLiabilities'],
                total_liabilites=statement_2124.loc[filed_date, 'TotalLiabilitiesNetMinorityInterest'],
                stockholders_equity=statement_2124.loc[filed_date, 'StockholdersEquity'],
                net_inventory=statement_2124.loc[filed_date, 'Inventory'],
                net_accounts_receivables=statement_2124.loc[filed_date, 'AccountsReceivable']

            )

            session.add(statement)
            session.commit()

    years = [d.year for d in statement_2124.index]
    return {"Balance Sheet Added": f"{min(years)} to {max(years)} of {ticker} added"}

