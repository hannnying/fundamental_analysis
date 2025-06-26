# run from fastAPI directory

from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet
from fastapi import FastAPI

app = FastAPI()

@app.get("/revenue/{ticker}")
async def get_ticker_revenue(ticker:str):
    results = (
        session.query(
            IncomeStatement.ticker,
            IncomeStatement.fiscal_year,
            IncomeStatement.revenue
        ).filter(IncomeStatement.ticker==ticker).all()
    )

    return [
        {
            "fiscal_year": r.fiscal_year,
            "revenue": r.revenue,
            "ticker": r.ticker
        }
        for r in results
    ]


def get_rival_tickers(ticker: str):
    sector = session.query(Company.sector).filter(Company.ticker==ticker).scalar_subquery()
    rivals = session.query(Company.ticker).filter(Company.sector==sector).all()
    return [r.ticker for r in rivals if r.ticker != ticker.upper()]


def get_rival_financials(tickers: list[str]):
    rival_financials = session.query(IncomeStatement).filter(IncomeStatement.ticker.in_(tickers))
    return rival_financials.all()


@app.get("/compare/{ticker}")
def compare_stock_to_rivals(ticker: str):
    rivals = get_rival_tickers(ticker)
    all_tickers = [ticker.upper()] + rivals
    financials = get_rival_financials(all_tickers)
    results = session.query(financials).order_by(IncomeStatement.basic_eps.desc()).all()

    return [
        {
            "fiscal_year": r.fiscal_year,
            "ticker": r.ticker,
            "basic_eps": r.basic_eps
        }
        for r in results
    ]




@app.get("/rival/{ticker}")
async def get_rival(ticker:str):
    sector_query = session.query(Company.sector).filter(Company.ticker==ticker).scalar_subquery()
    results = session.query(IncomeStatement).join(Company, IncomeStatement.ticker == Company.ticker).filter(Company.sector==sector_query).all()
    
    return [
        {
            "fiscal_year": r.fiscal_year,
            "ticker": r.ticker,
            "revenue": r.revenue,
            "cost_of_revenue": r.cost_of_revenue,
            "basic_eps": r.basic_eps,
        }
        for r in results
    ]

