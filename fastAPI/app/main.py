# run from fastAPI directory
import os
import app.stock as stock
import app.rivals as rivals
from app.utils import convert_to_dict
from internal.database import session
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import yfinance as yf

app = FastAPI()

# Allow frontend to call backend APIs
app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
)

# Mount the static frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/")
async def serve_frontend():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/company/financial-ratios")
async def financial_ratios(ticker:str):
    print(f"Received ticker: {ticker}")
    financial_ratio_query = stock.get_raw_all_ratios(ticker).all()
    return convert_to_dict(financial_ratio_query)


@app.get("/company/market")
async def compare_price_spy(ticker:str):
    print(f"Received ticker: {ticker}")
    ticker_prices = yf.Ticker(ticker).history(period='1y').loc[:,"Close"]
    spy_prices = yf.Ticker("SPY").history(period="1y").loc[:,"Close"]

    return {
        ticker: f"{round(100 * (ticker_prices.iloc[0] - ticker_prices.iloc[-1]) / ticker_prices.iloc[-1], 2)}%",
        "SPY": f"{round(100 * (spy_prices.iloc[0] - spy_prices.iloc[-1]) / spy_prices.iloc[-1], 2)}%",
    }


@app.get("/sector/financials")
async def sector_financials(ticker:str):
    sector_financials_query = rivals.get_rival_financials(ticker)
    return convert_to_dict(sector_financials_query)


@app.get("/sector/compare")
async def sector_compare_ratios(ticker:str):
    print(f"Received ticker: {ticker}")
    sector_ratios_query = rivals.compare_sector_averages(ticker).subquery()
    stock_ratios_query = stock.get_raw_all_ratios(ticker).subquery()
    results = (
        session.query(
            sector_ratios_query.c.fiscal_year,
            sector_ratios_query.c.basic_eps.label("sector_basic_eps"),
            stock_ratios_query.c.basic_eps.label(f"{ticker}_basic_eps"),
            sector_ratios_query.c.profit_margin.label("sector_profit_margin"),
            stock_ratios_query.c.profit_margin.label(f"{ticker}_profit_margin"),
            sector_ratios_query.c.operating_margin.label("sector_operating_margin"),
            stock_ratios_query.c.operating_margin.label(f"{ticker}_operating_margin"),
            sector_ratios_query.c.current_ratio.label("sector_current_ratio"),
            stock_ratios_query.c.current_ratio.label(f"{ticker}_current_ratio"),
            sector_ratios_query.c.debt_to_equity.label("sector_debt_to_equity"),
            stock_ratios_query.c.debt_to_equity.label(f"{ticker}_debt_to_equity"),
            sector_ratios_query.c.debt_to_assets.label("sector_debt_to_assets"),
            stock_ratios_query.c.debt_to_assets.label(f"{ticker}_debt_to_assets")
    )
    .join(stock_ratios_query, sector_ratios_query.c.fiscal_year==stock_ratios_query.c.fiscal_year)
    .order_by(sector_ratios_query.c.fiscal_year)
    .all()
    )
    
    return convert_to_dict(results)

