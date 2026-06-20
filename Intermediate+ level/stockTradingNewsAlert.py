import smtplib
import time
import requests
import yfinance as yf
from email.mime.text import MIMEText

STOCKS = {
    "TSLA": {"name": "Tesla Inc", "threshold": 5.0},
    "AAPL": {"name": "Apple Inc", "threshold": 3.0},
    "GOOGL": {"name": "Alphabet Inc", "threshold": 3.0},
}

NEWS_API_KEY = "https://newsapi.org"
NEWS_API_URL = "https://newsapi.org/v2/everything"
NEWS_PAGE_SIZE = 3

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"
RECIPIENT_EMAIL = "recipient_email@gmail.com"

CHECK_INTERVAL = 3600


def get_price_change(symbol: str) -> float | None:
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")
        if len(hist) < 2:
            print(f"Not enough history for {symbol}")
            return None
        closes = hist["Close"]
        yesterday_close = closes.iloc[-2]
        today_close = closes.iloc[-1]
        change_pct = ((today_close - yesterday_close) / yesterday_close) * 100
        print(f"{symbol}: {yesterday_close:.2f} -> {today_close:.2f} ({change_pct:+.2f}%)")
        return round(change_pct, 2)
    except Exception as e:
        print(f"Failed to get price for {symbol}: {e}")
        return None


def fetch_news(company_name: str) -> list[dict]:
    params = {
        "q": company_name,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": NEWS_PAGE_SIZE,
        "apiKey": NEWS_API_KEY,
    }
    try:
        resp = requests.get(NEWS_API_URL, params=params, timeout=10)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])
        return [
            {"title": a["title"], "description": a.get("description", ""), "url": a["url"]}
            for a in articles
        ]
    except requests.RequestException as e:
        print(f"Failed to fetch news for {company_name}: {e}")
        return []


def send_alert(symbol: str, change: float, articles: list[dict]) -> bool:
    direction = "📈 up" if change > 0 else "📉 down"
    subject = f"{symbol} {direction} {abs(change):.1f}% — News Alert"

    body_lines = [f"{symbol} moved {direction} by {abs(change):.1f}% today.\n"]
    if articles:
        body_lines.append("Top headlines:\n")
        for i, article in enumerate(articles, 1):
            body_lines.append(f"{i}. {article['title']}")
            if article.get("description"):
                body_lines.append(f"   {article['description']}")
            body_lines.append(f"   {article['url']}\n")
    else:
        body_lines.append("No related news found.\n")

    msg = MIMEText("\n".join(body_lines))
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"Alert sent for {symbol} ({direction} {abs(change):.1f}%)")
        return True
    except smtplib.SMTPAuthenticationError:
        print("SMTP authentication failed. Check your email/password.")
    except smtplib.SMTPException as e:
        print(f"Failed to send alert: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False


def process_stock(symbol: str, name: str, threshold: float):
    print(f"\nChecking {symbol} ({name})...")
    change = get_price_change(symbol)
    if change is None:
        return

    if abs(change) >= threshold:
        print(f"Threshold of {threshold}% exceeded! Fetching news...")
        articles = fetch_news(name)
        send_alert(symbol, change, articles)
    else:
        print(f"Change {change:+.2f}% within threshold ({threshold}%). Skipping.")


def main():
    print("Stock Trading News Alert started.")
    print(f"Monitoring: {', '.join(STOCKS.keys())}")
    print(f"Check interval: {CHECK_INTERVAL}s\n")

    while True:
        for symbol, info in STOCKS.items():
            process_stock(symbol, info["name"], info["threshold"])

        print(f"\nSleeping for {CHECK_INTERVAL}s...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
