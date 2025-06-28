# run from fastAPI directory
import app.stock as stock
import app.rivals as rivals
from app.utils import convert_to_dict
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


@app.get("/financial-ratios/{ticker}")
async def financial_ratios(ticker:str):
    financial_ratio_query = stock.get_all_ratios(ticker)
    return financial_ratio_query



@app.get("/rival-financials/{ticker}")
async def rival_financials(ticker:str):
    rival_financials_query = rivals.get_rival_financials(ticker)
    return convert_to_dict(rival_financials_query)


@app.get("/rival-compare/{ticker}")
async def rival_eps(ticker:str):
    ticker_eps = (
        session.query(
            IncomeStatement.fiscal_year,
            IncomeStatement.basic_eps.label('basic_eps')
        ).filter(IncomeStatement.ticker==ticker).all()
    )
    # for now, compare_rivals only calculates average eps of sector
    sector_eps = rivals.compare_rivals(ticker).subquery()
    results = []
    for q in ticker_eps:
        result = {
            "fiscal_year": q.fiscal_year,
            f"{ticker}_eps": q.basic_eps,
            f"sector eps": session.query(sector_eps.c.sector_eps).filter(sector_eps.c.fiscal_year==q.fiscal_year).scalar()
        }
        results.append(result)
    return results
