# helper functions to retrieve metrics for the input stock
from app.utils import join_financials
from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet
from sqlalchemy import case, func
from sqlalchemy.orm import Query


def get_raw_ticker_join_financials(ticker):
    return join_financials().filter(IncomeStatement.ticker==ticker)


def get_ticker_join_financials(ticker):
    return (
        join_financials()
        .filter(IncomeStatement.ticker==ticker)
        .all()
    )
   

def calculate_profit_margin(row):
    return row.gross_profit / row.revenue if row.revenue else None

def calculate_operating_margin(row):
    return row.operating_income / row.revenue if row.revenue else None

def calculate_eps(row):
    return row.basic_eps

def calculate_current_ratio(row):
    return row.current_assets / row.current_liabilities if row.current_liabilities else None

def calculate_debt_to_equity(row):
    return row.total_liabilites / row.stockholders_equity if row.stockholders_equity else None

def calculate_debt_to_assets(row):
    return row.total_liabilites / row.total_assets if row.total_assets else None


def get_raw_all_ratios(ticker: str) -> Query:
    q = get_raw_ticker_join_financials(ticker).subquery()

    return session.query(
            q.c.fiscal_year,
            q.c.basic_eps,

            case(
                (q.c.revenue != 0, func.round(q.c.gross_profit / q.c.revenue, 2)),
                else_=None
            ).label("profit_margin"),

            case(
                (q.c.revenue != 0, func.round(q.c.operating_income / q.c.revenue, 2)),
                else_=None
            ).label("operating_margin"),

            case(
                (q.c.current_liabilities != 0, func.round(q.c.current_assets / q.c.current_liabilities, 2)),
                else_=None
            ).label("current_ratio"),

            case(
                (q.c.stockholders_equity != 0, func.round(q.c.total_liabilites / q.c.stockholders_equity, 2)),
                else_=None
            ).label("debt_to_equity"),

            case(
                (q.c.total_assets != 0, func.round(q.c.total_liabilites / q.c.total_assets, 2)),
                else_=None
            ).label("debt_to_assets")
        )