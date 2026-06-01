import yfinance as yf
import pandas as pd
from datetime import datetime
import os

tickers = ["RIOT", "MARA", "HUT", "CIFR", "BITF", "CLSK", "NBIS"]

csv_file = "YahooData.csv"

# Load existing CSV if it exists
if os.path.exists(csv_file):
    df_old = pd.read_csv(csv_file, parse_dates=["Last Updated"])
else:
    df_old = pd.DataFrame()

rows = []

for symbol in tickers:
    t = yf.Ticker(symbol)
    info = t.info

    current_price = info.get("currentPrice")
    day_high = info.get("dayHigh")
    day_low = info.get("dayLow")
    volume = info.get("volume")

    # Price change vs previous value
    prev_price = None
    if not df_old.empty:
        df_prev_symbol = df_old[df_old["Ticker"] == symbol]
        if not df_prev_symbol.empty:
            prev_price = df_prev_symbol["Current Price"].iloc[-1]
    price_change = current_price - prev_price if prev_price is not None else None

    # Analyst recommendations (last 30 days)
    try:
        rec_df = t.recommendations
        if rec_df is not None and not rec_df.empty:
            rec_df.index = pd.to_datetime(rec_df.index)
            cutoff_rec = datetime.utcnow() - pd.Timedelta(days=30)
            recent = rec_df[rec_df.index >= cutoff_rec]
            counts = recent['To Grade'].value_counts()
            strong_buy = counts.get('Strong Buy', 0)
            buy = counts.get('Buy', 0)
            hold = counts.get('Hold', 0)
            underperform = counts.get('Underperform', 0)
            sell = counts.get('Sell', 0)
        else:
            strong_buy = buy = hold = underperform = sell = 0
    except:
        strong_buy = buy = hold = underperform = sell = 0

    rows.append({
        "Ticker": symbol,
        "Current Price": current_price,
        "Price Change": price_change,
        "Day High": day_high,
        "Day Low": day_low,
        "Volume": volume,
        "Market Cap": info.get("marketCap"),
        "Trailing P/E": info.get("trailingPE"),
        "Forward P/E": info.get("forwardPE"),
        "Price/Sales (ttm)": info.get("priceToSalesTrailing12Months"),
        "Profit Margin": info.get("profitMargins"),
        "Revenue (ttm)": info.get("totalRevenue"),
        "Net Income (ttm)": info.get("netIncomeToCommon"),
        "Total Cash (mrq)": info.get("totalCash"),
        "Debt/Equity (mrq)": info.get("debtToEquity"),
        "Strong Buy": strong_buy,
        "Buy": buy,
        "Hold": hold,
        "Underperform": underperform,
        "Sell": sell,
        "Last Updated": datetime.utcnow()
    })

# Combine old data with new data
df_new = pd.DataFrame(rows)
df_combined = pd.concat([df_old, df_new], ignore_index=True)

# Keep only the latest row per ticker
df_combined = df_combined.sort_values("Last Updated").groupby("Ticker", as_index=False).last()

# Export
df_combined.to_csv(csv_file, index=False)
df_combined.to_excel("YahooData.xlsx", index=False)

print("✅ Updated @", datetime.utcnow())
