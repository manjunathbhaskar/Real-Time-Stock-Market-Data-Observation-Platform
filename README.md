# Real-Time Stock Market Data Observation Platform

A real-time observability platform that monitors and analyzes requests to the YFinance API. Built with FastAPI for the backend, Prometheus for metrics collection and querying, and Grafana for data visualization. Each service runs in its own Docker container, enabling easy deployment and scaling with Docker Compose.

## Features
- Real-time and historical stock data via YFinance
- Prometheus metrics for monitoring API performance
- FastAPI backend with built-in API documentation
- Grafana dashboards for data visualization
- Containerized architecture using Docker

## Current Implementation and Local Setup Instructions

### Running FastAPI and Prometheus Together

1. **Start Docker Desktop**  
   Make sure Docker Desktop is running on your machine.

2. **Navigate to the backend directory and start the services**  
   ```bash
   cd backend/
   docker-compose up --build
   ```

   You should see output indicating both containers are building and attaching. Specifically:
   - **api-1**: Shows `uvicorn` running on port 8000, which means the FastAPI server is up and ready to handle requests.
   - **prometheus-1**: Shows 200 OK responses from the `/metrics` endpoint, confirming Prometheus is successfully scraping metrics from the FastAPI server.

3. **Accessing the Services Locally**  
   Once the containers are running, you can access the following services locally:
   - FastAPI: `http://localhost:8000`
   - Prometheus: `http://localhost:9090`

### Creating API Traffic for Prometheus Metrics

To generate some traffic and send requests to the YFinance API, use a script that sends multiple `curl` requests to the FastAPI service. Prometheus will automatically scrape metrics from these requests at 5-second intervals.

### Working Endpoints

Use uppercase stock tickers (e.g., `AAPL`, not `aapl`) for all requests.

**Health Check**
```bash
curl http://localhost:8000/ | jq '.'
```

**Stock Price**
```bash
curl http://localhost:8000/stock/AAPL/price | jq '.'
```

**Historical Data**  
Default 1-month data:
```bash
curl http://localhost:8000/stock/AAPL/historical | jq '.'
```

Custom period and interval:
```bash
curl "http://localhost:8000/stock/AAPL/historical?interval=1wk&period=1y" | jq '.'
```

**Company Info**
```bash
curl http://localhost:8000/stock/AAPL/info | jq '.'
```

**Dividends**
```bash
curl http://localhost:8000/stock/AAPL/dividends | jq '.'
```

**Earnings Data**
```bash
curl http://localhost:8000/stock/AAPL/earnings | jq '.'
```

### Testing Endpoints

You can test requests by running:
```bash
curl http://localhost:8000/stock/AAPL/price | jq '.' && echo -e "\n" && curl http://localhost:8000/stock/MSFT/price | jq '.' && echo -e "\n" && curl http://localhost:8000/stock/GOOGL/historical | jq '.'
```

This will show the price data for `AAPL` and `MSFT`, and historical data for `GOOGL` (with customizable time intervals).

## Metrics Implementation

FastAPI exposes Prometheus metrics at the `/metrics` endpoint. These metrics include:
- Request counts by endpoint
- Request latency measurements
- Stock symbol request frequency
- Stock price fetch latency
- Successful vs failed YFinance calls
- Number of unique symbols requested

### Using Prometheus

Once the containers are running, you can query metrics through the Prometheus web UI at `http://localhost:9090`. Below are some of the key metrics you're tracking:

1. **API Traffic Patterns**  
   Track total requests across all endpoints:
   ```bash
   market_data_requests_total
   ```

   This metric shows the breakdown of API usage, including price lookups, historical data pulls, and company info requests.

2. **Stock Symbol Analytics**  
   See which stocks are being queried the most:
   ```bash
   stock_symbol_requests_total
   ```

   This will show the request volume per stock symbol over time, such as for `AAPL`, `GOOGL`, and `MSFT`.

## Development Status

**Done**:
- YFinance API Integration
  - Real-time price endpoint
  - Historical data endpoint
  - Company info endpoint
  - Dividend data endpoint
  - Earnings data endpoint
- Docker:
  - FastAPI container
  - Prometheus container
  - Docker Compose setup
- Prometheus metrics:
  - Request counting
  - Latency tracking
  - Error monitoring
  - YFinance call success rate

**In Progress**:
- Grafana integration (dashboards and visualization)

## Requirements
- Python 3.9 or newer
- Docker Desktop (for containerized deployment)

## License
MIT License – feel free to use, modify, and distribute as you wish!

