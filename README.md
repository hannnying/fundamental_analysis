# SEC Filings JSON Extractor

This project is designed to process and standardize financial data from SEC 10-K filings. It extracts relevant financial statements from JSON files and converts them into structured tables for downstream analysis or database insertion.

---

## 📁 Project Structure
project/
├── data/
│   └── sec_filings/          # Cached SEC 10-K filings in JSON format
│       └── {ticker}_{fiscal_year}_10-K.json
├── extract/                  # Python modules for parsing and table creation
│   ├── balance_sheet.py
│   ├── company.py
│   ├── filings.py
│   ├── income_statement.py
│   ├── utils.py
│   ├── view.py
└── README.md

## 🗂 Dependencies

This project primarily uses:
- pandas 
- sec_api
- sec_cik_mapper
- sqlalchemy
- yfinance

