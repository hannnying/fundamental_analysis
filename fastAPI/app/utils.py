from internal.database import session
from internal.models import IncomeStatement, BalanceSheet, Company
from sqlalchemy.orm import Query

i = IncomeStatement
b = BalanceSheet
c = Company

def convert_to_dict(query:Query):
    return [q._asdict() for q in query]


def join_financials():
    """SELECT * FROM income_statement i JOIN balance_sheet b ON
    i.ticker = b.ticker and i.fiscal_year = b.fiscal_year
    WHERE i.ticker = ticker
    """

    return session.query(
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
        ).join(b, (i.ticker == b.ticker) & (i.fiscal_year == b.fiscal_year)
        ).filter(i.revenue != None) # exclude year where data isn't available       


def get_ticker_sector(ticker:str):
    return session.query(c.sector).filter(c.ticker == ticker).scalar_subquery()


