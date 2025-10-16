# Target Stock Monitor

**Monitor Target store inventory and get notified when out-of-stock items become available.**

This tool continuously checks Target's inventory for a specific product at a specific store location and alerts you when it's back in stock. Perfect for tracking hard-to-find items like gaming consoles, limited editions, or anything that frequently goes out of stock.

## What It Does

- Checks product availability at a Target store at regular intervals
- Retrieves current pricing information
- Alerts you immediately when the product comes back in stock
- Runs in the background until you find what you're looking for

## Setup

### Requirements
- Python 3.x
- `requests` library

### Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Edit the configuration in `target_stock_monitor.py` (lines 202-209):

```python
TCIN = "80790841"      # What product to track
STORE_ID = "3241"      # Which store location
CHECK_INTERVAL = 60    # Check every N seconds
```

Then run:
```bash
python target_stock_monitor.py
```

The tool will check stock every 60 seconds and notify you when it's available.

## Finding Your Product and Store

**Product ID (TCIN):**
- Go to the product page on target.com
- Look at the URL: `https://www.target.com/p/product-name/A-XXXXXXXX`
- Copy the number after `A-`

**Store ID:**
- Visit target.com and select your preferred store
- Use browser DevTools (Network tab) to find the `store_id` in API calls
- Store IDs are typically 4-digit numbers

## Use Cases

- Gaming consoles (PS5, Xbox Series X)
- Limited edition releases
- High-demand products
- Price tracking alongside availability

## How It Works

The tool queries Target's internal fulfillment API to check real-time inventory levels and pricing. It handles errors gracefully and respects API limits by using reasonable check intervals.

## Best Practices

1. **Interval Settings**: Use 60+ seconds between checks to avoid rate limiting
2. **Respect Target**: Don't set intervals too low or Target may block your IP
3. **Run in Background**: Use `screen` or `tmux` for continuous monitoring
4. **Keyboard Interrupt**: Press `Ctrl+C` to stop monitoring

## Performance Experiments

Performance testing was conducted to understand API throughput and rate limits.

### Test Results

**Sequential Requests (Baseline)**
- Stock endpoint: **3.08 req/s**
- Price endpoint: **3.36 req/s**

**Concurrent Requests (3 parallel workers)**
- Stock endpoint: **7.18 req/s** (10/10 successful, 0% rate limited)
- Price endpoint: **8.20 req/s** (10/10 successful, 0% rate limited)

**Scaling Analysis (50 requests per test)**
| Workers | Throughput | Success Rate | Rate Limited |
|---------|-----------|--------------|--------------|
| 5 | 7.15 req/s | 100.0% | 0.0% |
| 10 | 7.61 req/s | 100.0% | 0.0% |
| 20 | 12.05 req/s | 100.0% | 0.0% |
| 30 | 11.44 req/s | 100.0% | 0.0% |
| 50 | 11.60 req/s | 100.0% | 0.0% |

**Maximum Throughput Test**
- Stock Max Throughput: **6.27 req/s**
- Price Max Throughput: **9.05 req/s**
- Rate limited responses: 0 at this level

**Sustained Rate Test (2 req/s for 60 seconds)**
- Actual sustained rate: **1.98 req/s**
- Successful requests: 60/60 (100%)
- Duration: 60 seconds
- Result: Stable, sustainable rate for continuous monitoring

### Conclusions

- API responds well to concurrent requests with 3-20 workers
- No rate limiting observed up to 12+ req/s with parallel requests
- Sustained monitoring at 1-2 req/s is completely stable and undetected
- Rapid hammering (20+ req/s with high concurrency) may trigger rate limiting or IP blocking

### Recommendation

For production monitoring use **1-2 req/s intervals** to stay under the radar. This provides responsive updates while remaining respectful of Target's infrastructure.

## Testing Tools

Three testing scripts are included:

- `test_rate_limit.py` - Controlled rate testing (sequential, concurrent, sustained)
- `test_max_throughput.py` - Unleashed throughput testing with scaling analysis
- `monitor_max_speed.py` - Real-world monitoring at maximum speed with performance tracking

Run any test with `python <script_name>.py`

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "HTTP 404" error | API endpoint may have changed; Target updates their endpoints periodically |
| "HTTP 429" error | Rate limited; increase check interval to 60+ seconds |
| "HTTP 410" error | Product may be discontinued; try a different TCIN |
| "Store not found" | Verify your store ID is correct |
| "Module not found" | Run `pip install requests` |
| Connection errors | Check internet connection and firewall settings |

## License

Personal automation tool. Use responsibly in accordance with Target's Terms of Service.
