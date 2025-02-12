from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import yfinance as yf
from datetime import datetime

router = APIRouter(prefix="/stock", tags=["options"])

@router.get("/{ticker}/options")
async def get_options_chain(
    ticker: str,
    date: Optional[str] = Query(None, description="Expiration date (YYYY-MM-DD). If not provided, returns all available dates")
):
    """
    Get the options chain (calls and puts) for a specific ticker symbol. 
    If no expiration date is provided, returns all available expiration dates. 
    If a specific date is provided, returns the options for that date.
    """
    try:
        stock = yf.Ticker(ticker)
        
        # If no expiration date is provided, list all available dates
        if date is None:
            dates = stock.options
            if not dates:
                return {"ticker": ticker, "options_dates": []}
            return {
                "ticker": ticker,
                "options_dates": [str(d) for d in dates]
            }
        
        # If a specific expiration date is provided, get the options chain for that date
        if date not in stock.options:
            raise HTTPException(status_code=404, detail=f"Expiration date {date} not found for {ticker}")
        
        options_chain = stock.option_chain(date)
        
        # Check if the options data is empty
        if options_chain.calls.empty and options_chain.puts.empty:
            raise HTTPException(status_code=404, detail=f"No options data found for {ticker} on {date}")
        
        # Return the options chain data
        return {
            "ticker": ticker,
            "expiration": date,
            "calls": options_chain.calls.to_dict(orient='records'),
            "puts": options_chain.puts.to_dict(orient='records')
        }
    
    except Exception as e:
        # Provide detailed error message in case of failure
        raise HTTPException(status_code=400, detail=f"Error fetching options data: {str(e)}")
