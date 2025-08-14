from app.utils import get_ticker_sector, join_financials
from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet
from sqlalchemy import func, case
from sqlalchemy.orm import Query

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


def compare_sector_averages(ticker: str) -> Query:
    rival_query = get_raw_rival_financials(ticker).subquery()

    return session.query(
    rival_query.c.fiscal_year,

    func.round(
        func.avg(
            case(
                (rival_query.c.revenue != 0, rival_query.c.gross_profit / rival_query.c.revenue),
                else_=None
            )
        ), 2
    ).label("profit_margin"),

    func.round(
        func.avg(
            case(
                (rival_query.c.revenue != 0, rival_query.c.operating_income / rival_query.c.revenue),
                else_=None
            )
        ), 2
    ).label("operating_margin"),

    func.round(
        func.avg(rival_query.c.basic_eps), 2
    ).label("basic_eps"),

    func.round(
        func.avg(
            case(
                (rival_query.c.current_liabilities != 0,
                 rival_query.c.current_assets / rival_query.c.current_liabilities),
                else_=None
            )
        ), 2
    ).label("current_ratio"),

    func.round(
        func.avg(
            case(
                (rival_query.c.stockholders_equity != 0,
                 rival_query.c.total_liabilites / rival_query.c.stockholders_equity),
                else_=None
            )
        ), 2
    ).label("debt_to_equity"),

    func.round(
        func.avg(
            case(
                (rival_query.c.total_assets != 0,
                 rival_query.c.total_liabilites / rival_query.c.total_assets),
                else_=None
            )
        ), 2
    ).label("debt_to_assets"),
).group_by(rival_query.c.fiscal_year)
