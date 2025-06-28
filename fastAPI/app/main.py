# run from fastAPI directory
import app.stock as stock
import app.rivals as rivals
from app.utils import convert_to_dict
from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet
from fastapi import FastAPI

app = FastAPI()


@app.get("/company/financial-ratios")
async def financial_ratios(ticker:str):
    financial_ratio_query = stock.get_raw_all_ratios(ticker).all()
    return convert_to_dict(financial_ratio_query)


@app.get("/sector/financials")
async def sector_financials(ticker:str):
    sector_financials_query = rivals.get_rival_financials(ticker)
    return convert_to_dict(sector_financials_query)


@app.get("/sector/compare")
async def sector_compare_ratios(ticker:str):
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

