from fastapi import FastAPI, HTTPException, Query
from typing import Optional, Dict
from datetime import datetime
import yfinance as yf
from .routes import options
from .metrics import (
    PrometheusMiddleware,
    track_symbol_request,
    track_yfinance_operation,
    metrics_endpoint,
    YFINANCE_CALLS
)

app = FastAPI(title="Market Data API")

# Add Prometheus middleware for tracking metrics
app.add_middleware(PrometheusMiddleware)

# Include options router
app.include_router(options.router)

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    return await metrics_endpoint()

# Health check endpoint
@app.get("/")
async def health_check():
    """Health check endpoint to verify if the API is running."""
    return {"status": "online", "timestamp": datetime.now().isoformat()}

# Reusable function to fetch stock data
async def fetch_stock_data(ticker: str):
    """Helper function to fetch the stock data using yfinance."""
    stock = yf.Ticker(ticker)
    return stock

# Core endpoints

@app.get("/stock/{ticker}/price")
async def get_current_price(ticker: str):
    """Get the latest stock price and volume data for a single ticker."""
    try:
        track_symbol_request(ticker)
        with YFINANCE_CALLS.labels(operation='get_price').time():
            stock = await fetch_stock_data(ticker)
            data = stock.history(period='1d')
            if data.empty:
                raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
            return {
                "ticker": ticker,
                "current_price": float(data['Close'].iloc[-1]),
                "volume": int(data['Volume'].iloc[-1]),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock/{ticker}/historical")
async def get_historical_data(
    ticker: str,
    interval: str = Query(default='1d', description="Data interval (1d, 1wk, 1mo)"),
    period: str = Query(default='1mo', description="Historical period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
):
    """Get historical price data with customizable intervals and time periods."""
    try:
        track_symbol_request(ticker)
        with YFINANCE_CALLS.labels(operation='get_historical').time():
            stock = await fetch_stock_data(ticker)
            history = stock.history(period=period, interval=interval)
        
        if history.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for ticker {ticker}")
            
        return {
            "ticker": ticker,
            "interval": interval,
            "period": period,
            "data_points": len(history),
            "history": history.to_dict(orient='index')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock/{ticker}/info")
async def get_company_info(ticker: str):
    """Get company profile and information."""
    try:
        track_symbol_request(ticker)
        with YFINANCE_CALLS.labels(operation='get_info').time():
            stock = await fetch_stock_data(ticker)
            info = stock.info
        
        essential_info = {
            "ticker": ticker,
            "company_info": {
                "longName": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "website": info.get("website"),
                "marketCap": info.get("marketCap"),
                "employees": info.get("fullTimeEmployees"),
                "country": info.get("country"),
                "city": info.get("city"),
                "summary": info.get("longBusinessSummary"),
                "currency": info.get("currency"),
                "exchange": info.get("exchange")
            }
        }
        return essential_info
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock/{ticker}/dividends")
async def get_dividend_data(ticker: str):
    """Get dividend history for a company."""
    try:
        track_symbol_request(ticker)
        with YFINANCE_CALLS.labels(operation='get_dividends').time():
            stock = await fetch_stock_data(ticker)
            dividends = stock.dividends
        if dividends.empty:
            return {"ticker": ticker, "dividend_history": "No dividend data available"}
        return {
            "ticker": ticker,
            "dividend_history": dividends.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stock/{ticker}/earnings")
async def get_earnings_data(
    ticker: str,
    frequency: str = Query(default='yearly', description="Data frequency (yearly or quarterly)")
):
    """Get earnings data for a company."""
    try:
        track_symbol_request(ticker)
        with YFINANCE_CALLS.labels(operation='get_earnings').time():
            stock = await fetch_stock_data(ticker)
            earnings = stock.earnings(frequency=frequency)
            if earnings.empty:
                return {"ticker": ticker, "earnings_data": "No earnings data available"}
            return {
                "ticker": ticker,
                "frequency": frequency,
                "earnings_data": earnings.to_dict()
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stocks/batch")
async def get_multiple_stocks(
    tickers: str = Query(..., description="Comma-separated list of tickers (e.g., AAPL,MSFT,GOOGL)")
):
    """Get current price for multiple stocks."""
    try:
        ticker_list = tickers.split(',')
        stocks = yf.Tickers(' '.join(ticker_list))
        
        results = {}
        for ticker in ticker_list:
            try:
                data = stocks.tickers[ticker].history(period='1d')
                if not data.empty:
                    results[ticker] = {
                        "current_price": data['Close'].iloc[-1],
                        "volume": data['Volume'].iloc[-1]
                    }
                else:
                    results[ticker] = {"error": "No data found"}
            except Exception as e:
                results[ticker] = {"error": f"Failed to fetch data: {str(e)}"}
                
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
