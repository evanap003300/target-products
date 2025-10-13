# Target Product Stock Monitor

Automatically monitor Target product availability and get notified when items are back in stock.

## Features

- Real-time stock monitoring for any Target product
- Configurable check intervals
- Robust error handling (network errors, rate limiting, API failures)
- Easy configuration for different products and store locations
- Continuous monitoring until product is in stock

## Requirements

- Python 3.x
- `requests` library

## Installation

1. Install the required dependency:
```bash
pip install requests
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Quick Start

### Test Single Check

Run a single stock check to verify everything is working:

```bash
python test_target_api.py
```

### Start Monitoring

Run the continuous monitor:

```bash
python target_stock_monitor.py
```

The monitor will check stock every 60 seconds (default) and alert you when the product is available.

## Configuration

Edit the configuration variables in `target_stock_monitor.py` (lines 202-209):

```python
# Configuration - Modify these values to monitor different products/stores
TCIN = "80790841"  # Product TCIN
STORE_ID = "3241"  # Store ID
CHECK_INTERVAL = 60  # Seconds between checks (60s = 1 minute)

# Optional: ZIP and location for the store
ZIP_CODE = "27599"
STATE = "NC"
LATITUDE = "35.930"
LONGITUDE = "-79.040"
```

### Finding Product Information

**TCIN (Target Product ID):**
- Visit the product page on target.com
- Look at the URL: `https://www.target.com/p/product-name/A-XXXXXXXX`
- The TCIN is the number after `A-` (e.g., 87576259)

**Store ID:**
- Visit target.com and set your preferred store
- Use browser developer tools (Network tab) to find the `store_id` parameter in API requests
- Common store IDs are 4-digit numbers (e.g., 3241 for UNC Franklin St)

## Usage Examples

### Example 1: Monitor with default settings

```python
from target_stock_monitor import TargetStockMonitor

monitor = TargetStockMonitor(tcin="87576259", store_id="3241")
monitor.monitor(check_interval=60)  # Check every 60 seconds
```

### Example 2: Check stock once

```python
from target_stock_monitor import TargetStockMonitor

monitor = TargetStockMonitor(tcin="87576259", store_id="3241")
stock_info = monitor.check_stock()

if stock_info and stock_info["in_stock"]:
    print(f"IN STOCK! Quantity: {stock_info['quantity']}")
else:
    print("Out of stock")
```

### Example 3: Custom check interval and max attempts

```python
from target_stock_monitor import TargetStockMonitor

monitor = TargetStockMonitor(tcin="87576259", store_id="3241")
# Check every 2 minutes, maximum 100 attempts
monitor.monitor(check_interval=120, max_attempts=100)
```

## How It Works

1. **API Request**: Sends GET request to Target's fulfillment API with product and store information
2. **Response Parsing**: Extracts stock quantity from the JSON response
3. **Stock Check**: Compares quantity to zero to determine availability
4. **Monitoring Loop**: Continuously checks at specified intervals until stock is found
5. **Error Handling**: Gracefully handles network errors, rate limiting, and API failures

## API Response Structure

The script parses this path from Target's API:
```
data.product.fulfillment.store_options[].location_available_to_promise_quantity
```

Example response for a store:
```json
{
  "location_id": "3241",
  "store": {
    "location_name": "UNC Franklin St"
  },
  "location_available_to_promise_quantity": 0.0
}
```

## Error Handling

The monitor handles various error scenarios:

- **429 (Rate Limited)**: Waits for next check interval
- **403 (Forbidden)**: May indicate blocked user agent or invalid API key
- **503 (Service Unavailable)**: Target servers temporarily down
- **Network Errors**: Connection timeouts, DNS failures, etc.
- **Parse Errors**: Invalid JSON or unexpected response structure

## Output Example

```
[2025-10-13 14:30:15] Starting stock monitor for TCIN: 87576259
[2025-10-13 14:30:15] Checking store: 3241
[2025-10-13 14:30:15] Check interval: 60 seconds
------------------------------------------------------------
[2025-10-13 14:30:15] Attempt #1: Checking stock...
[2025-10-13 14:30:16] Out of stock at UNC Franklin St. Waiting 60s...
[2025-10-13 14:31:16] Attempt #2: Checking stock...
[2025-10-13 14:31:17] Out of stock at UNC Franklin St. Waiting 60s...
...
[2025-10-13 15:45:23] Attempt #75: Checking stock...

============================================================
[2025-10-13 15:45:24] 🎯 IN STOCK! 🎯
Location: UNC Franklin St
Quantity: 3
Store ID: 3241
TCIN: 87576259
============================================================
```

## Best Practices

1. **Check Interval**: Use 60 seconds or longer to avoid rate limiting
2. **Respectful Monitoring**: Don't set intervals too low (Target may block your IP)
3. **Run in Background**: Use `screen` or `tmux` for long-running monitors
4. **Multiple Products**: Run separate instances for different products

## Stopping the Monitor

- Press `Ctrl+C` to gracefully stop the monitor
- The monitor automatically stops when product is found in stock

## Troubleshooting

**"HTTP 410 Gone" error:**
- Product TCIN may be discontinued
- Try a different TCIN

**"Store not found in response":**
- Verify the store_id is correct
- Check that the store location matches the ZIP/coordinates

**"Module 'requests' not found":**
- Install requests: `pip install requests`

**Connection errors:**
- Check internet connection
- Verify firewall/proxy settings

## Files

- `target_stock_monitor.py` - Main monitoring script
- `test_target_api.py` - Single check test script
- `debug_target_api.py` - Detailed debugging output
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## License

This is a personal automation tool. Use responsibly and in accordance with Target's Terms of Service.
