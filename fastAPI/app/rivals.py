from app.utils import get_ticker_sector, join_financials
from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet
from sqlalchemy import func

def get_raw_rival_financials(ticker: str):
    sector_subquery = get_ticker_sector(ticker)
    all_financials_query = join_financials()

    return all_financials_query.join(Company, IncomeStatement.ticker==Company.ticker).filter(Company.sector==sector_subquery)


def get_rival_financials(ticker: str):
    sector_subquery = get_ticker_sector(ticker)
    all_financials_query = join_financials()

    return (
        all_financials_query
        .join(Company, IncomeStatement.ticker==Company.ticker)
        .filter(Company.sector==sector_subquery)
        .order_by(IncomeStatement.fiscal_year)
        .all()
    )


def compare_rivals(ticker: str,):
    rival_financials_query = get_raw_rival_financials(ticker).subquery()
    return session.query(
            rival_financials_query.c.fiscal_year,
            func.avg(rival_financials_query.c.basic_eps).label('sector_eps')
        ).group_by(rival_financials_query.c.fiscal_year)