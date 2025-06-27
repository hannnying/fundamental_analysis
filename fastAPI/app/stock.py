# helper functions to retrieve metrics for the input stock

from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet

def get_join_financials(ticker):
    """SELECT * FROM income_statement i JOIN balance_sheet b ON
    i.ticker = b.ticker and i.fiscal_year = b.fiscal_year
    WHERE i.ticker = ticker
    """
    i = IncomeStatement
    b = BalanceSheet

    return (
        session.query(
            i.fiscal_year,
            i.ticker,
            i.revenue,
            i.cost_of_revenue,
            i.net_income, 
            i.operating_income,
            i.gross_profit,
            i.basic_eps,
            b.current_assets,
            b.total_assets,
            b.current_liabilities,
            b.total_liabilites,
            b.current_assets,
            b.stockholders_equity
        ).join(b, (i.ticker == b.ticker) & (i.fiscal_year == b.fiscal_year))
        .filter(i.ticker == ticker)
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
    rows = get_join_financials(ticker)
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