# helper functions to retrieve metrics for the input stock
from app.utils import join_financials
from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet

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


def get_all_ratios(ticker):
    rows = get_ticker_join_financials(ticker)
    results = []

    for row in rows:
        metrics = {
            "ticker": row.ticker,
            "fiscal_year": row.fiscal_year,
            "profit_margin": calculate_profit_margin(row),
            "operating_margin": calculate_operating_margin(row),
            "eps": calculate_eps(row),
            "current_ratio": calculate_current_ratio(row),
            "debt_to_equity": calculate_debt_to_equity(row),
            "debt_to_assets": calculate_debt_to_assets(row),
        }
        results.append(metrics)
    return results