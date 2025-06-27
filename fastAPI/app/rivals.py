from internal.database import session
from internal.models import Company, IncomeStatement, BalanceSheet

"""SELECT * FROM income_statement i JOIN balance_sheet b 
ON i.ticker = b.ticker AND i.fiscal_year = b.fiscal_year
WHERE i.ticker IN (SELECT ticker FROM company WHERE ticker = input_ticker)"""

def fetch_rival_financials(ticker: str):
    i = IncomeStatement
    b = BalanceSheet
    c = Company

    sector_subquery = (
        session.query(c.sector)
        .filter(c.ticker == ticker)
        .scalar_subquery()
    )

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
            b.stockholders_equity
        )
        .join(b, (i.ticker == b.ticker) & (i.fiscal_year == b.fiscal_year))
        .join(c, i.ticker == c.ticker)
        .filter(c.sector == sector_subquery)
        .order_by(i.fiscal_year)
        .all()
    )


def get_rival_financials(ticker):
    rows = fetch_rival_financials(ticker)
    results = []

    for row in rows:
        rival = {
            "ticker": row.ticker,
            "fiscal_year": row.fiscal_year,
            "revenue": row.revenue,
            "cost_of_revenue": row.cost_of_revenue,
            "net_income": row.net_income, 
            "operating_income": row.operating_income,
            "gross_profit": row.gross_profit,
            "basic_eps": row.basic_eps,
            "current_assets": row.current_assets,
            "total_assets": row.total_assets,
            "current_liabilities": row.current_liabilities,
            "total_liabilities": row.total_liabilites,
            "stockholders_equity": row.stockholders_equity
        }
        results.append(rival)
    return results

# @app.get("/compare/{ticker}")
# def compare_stock_to_rivals(ticker: str):
#     rivals = get_rival_tickers(ticker)
#     all_tickers = [ticker.upper()] + rivals
#     financials = get_rival_financials(all_tickers)
#     results = session.query(financials).order_by(IncomeStatement.basic_eps.desc()).all()

#     return [
#         {
#             "fiscal_year": r.fiscal_year,
#             "ticker": r.ticker,
#             "basic_eps": r.basic_eps
#         }
#         for r in results
#     ]




# @app.get("/rival/{ticker}")
# async def get_rival(ticker:str):
#     sector_query = session.query(Company.sector).filter(Company.ticker==ticker).scalar_subquery()
#     results = session.query(IncomeStatement).join(Company, IncomeStatement.ticker == Company.ticker).filter(Company.sector==sector_query).all()
    
#     return [
#         {
#             "fiscal_year": r.fiscal_year,
#             "ticker": r.ticker,
#             "revenue": r.revenue,
#             "cost_of_revenue": r.cost_of_revenue,
#             "basic_eps": r.basic_eps,
#         }
#         for r in results
#     ]

