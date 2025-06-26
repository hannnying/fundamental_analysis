from sec_cik_mapper import StockMapper
from urllib.parse import urlparse
import warnings
from models import Company, IncomeStatement, BalanceSheet
import yfinance as yf

mapper = StockMapper()

def cik_to_ticker(cik):
    return list(mapper.cik_to_tickers[cik])[0]


def ticker_to_cik(ticker):
    return mapper.ticker_to_cik[ticker]


def get_cik_from_url(url):
    path_parts = urlparse(url).path.split('/')
    # The CIK is the 4th part after splitting by '/'
    # Example path: /Archives/edgar/data/1326801/000132680125000017/meta-12312024x10kexhibit191.htm
    try:
        cik = path_parts[4]
        leading_zeros = 10 - len(cik)
        return "0" * leading_zeros + cik
    except IndexError:
        return None


stock_tickers = ['NVDA', 'MSFT', 'AAPL', 'AMZN', 'GOOG', 'META',
                 'AVGO', 'TSLA', 'ORCL', 'NFLX', 'PLTR'] # improve: txt file, web scraping after handling certain companies whose financial statements may differ