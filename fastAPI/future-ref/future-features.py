@app.get("/market-analysis/")
async def get_market_analysis(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="3mo")  # longer period for moving averages

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for the given ticker")

        df["MA20"] = df["Close"].rolling(window=20).mean()
        df["MA50"] = df["Close"].rolling(window=50).mean()
        df["Sentiment"] = df["Close"].gt(df["MA50"]).map({True: "bullish", False: "bearish"})

        df = df.reset_index()  # Include date in output
        result = df[["Date", "Close", "MA20", "MA50", "Sentiment"]].dropna().to_dict(orient="records")
        
        return {
            "ticker": ticker,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Compare Stock Price Performance with S&P500

# Show trends in sales and costs to highlight growth or margin pressure

# Future Data Science Extensions

# Predict future earnings or sales trends based on historical data
# Cluster companies by financial health or growth profiles
# Recommend stocks based on fundamental strength
# Sentiment analysis combining news + fundamentals