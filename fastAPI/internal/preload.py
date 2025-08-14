from internal.database import session
from internal.models import BalanceSheet, Company, IncomeStatement
from internal.utils import ticker_to_cik, stock_tickers
import yfinance as yf

# from database import session
# from models import BalanceSheet, Company, IncomeStatement
# from utils import ticker_to_cik, stock_tickers
# import yfinance as yf


def retrieve_column(statement, filed_date, col_name):
    try:
        value = statement.loc[filed_date, col_name]
    except KeyError as e:
        print(f"[!] Missing data for ({filed_date}, {col_name}): handled with None.")
        value = None
    return value

def create_company(ticker:str):
    info = yf.Ticker(ticker.upper()).info
    cik = ticker_to_cik(ticker)
    name = info.get("longName")
    sector = info.get("sector")
    industry = info.get("industry")

    company = Company(
            ticker=ticker,
            cik=cik,
            name=name,
            sector=sector,
            industry=industry
    )

    existing = session.get(Company, ticker)
    if not existing:
        session.add(company)
        session.commit()
        print(f"Added {name} into companies.")
    else:
        print(f"{name} already exists in companies table.")


def create_income_statement(ticker:str):
    statement_2124 = yf.Ticker(ticker.upper()).get_income_stmt().T

    for filed_date in statement_2124.index:
        fiscal_year = filed_date.year
        if not session.get(IncomeStatement, (ticker, fiscal_year)):
            statement = IncomeStatement(
                ticker=ticker,
                fiscal_year=fiscal_year,
                revenue=retrieve_column(statement_2124, filed_date, "TotalRevenue"),
                cost_of_revenue=retrieve_column(statement_2124, filed_date, "CostOfRevenue"),
                net_income=retrieve_column(statement_2124, filed_date,"NetIncome"),
                operating_income=retrieve_column(statement_2124, filed_date,"OperatingIncome"),
                gross_profit=retrieve_column(statement_2124, filed_date, "GrossProfit"),
                basic_eps=retrieve_column(statement_2124, filed_date, "BasicEPS")
            )

            session.add(statement)
            session.commit()

    years = [d.year for d in statement_2124.index]
    print(f"Added income statement {min(years)} to {max(years)} of {ticker}")


def create_balance_sheet(ticker:str):
    statement_2124 = yf.Ticker(ticker.upper()).get_balance_sheet().T

    for filed_date in statement_2124.index:
        fiscal_year = filed_date.year
        if not session.get(BalanceSheet, (ticker, fiscal_year)):
            statement = BalanceSheet(
                ticker=ticker,
                fiscal_year=fiscal_year,
                cash_equivalents=retrieve_column(statement_2124, filed_date, "CashAndCashEquivalents"),
                current_assets=retrieve_column(statement_2124, filed_date, 'CurrentAssets'),
                total_assets=retrieve_column(statement_2124, filed_date, 'TotalAssets'),
                current_liabilities=retrieve_column(statement_2124, filed_date, 'CurrentLiabilities'),
                total_liabilites=retrieve_column(statement_2124, filed_date, 'TotalLiabilitiesNetMinorityInterest'),
                stockholders_equity=retrieve_column(statement_2124, filed_date, 'StockholdersEquity'),
                net_inventory=retrieve_column(statement_2124, filed_date,'Inventory'),
                net_accounts_receivables=retrieve_column(statement_2124, filed_date, 'AccountsReceivable')

            )

            session.add(statement)
            session.commit()

    years = [d.year for d in statement_2124.index]
    print(f"Added balance sheet from {min(years)} to {max(years)} of {ticker}")


def load_ticker(ticker:str):
    create_company(ticker)
    create_balance_sheet(ticker)
    create_income_statement(ticker)
    print("loaded {ticker} info into database")


if __name__ == "__main__":
    for ticker in stock_tickers:
        load_ticker(ticker)


