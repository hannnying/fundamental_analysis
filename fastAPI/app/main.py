# run from fastAPI directory
import app.stock as stock
import app.rivals as rivals
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
    return stock.get_all_ratios(ticker)



@app.get("/rival-financials/{ticker}")
async def rival_financials(ticker:str):
    return rivals.get_rival_financials(ticker)