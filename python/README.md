# Target Stock Monitor

**Monitor Target store inventory and get notified when out-of-stock items become available.**

This tool continuously checks Target's inventory for a specific product at a specific store location and alerts you when it's back in stock. Perfect for tracking hard-to-find items like gaming consoles, limited editions, or anything that frequently goes out of stock.

### Advanced Features

- **HTTP Browser Fingerprinting**: ✅ Proven effective - rotates User-Agent, Accept-Language, DNT headers
- **Session Management**: ✅ Proven effective - rotates visitor IDs to avoid session tracking
- **TLS Fingerprinting**: ⚠️ Experimental - JA3 profile matching available but results mixed
- **Throughput Analysis**: Comprehensive testing to identify actual rate limits vs. anti-bot blocking
- **Concurrent Request Support**: Scales from sequential to 50+ parallel workers with performance metrics

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

## Project Files

```
python/
├── target_stock_monitor.py         # Core monitoring engine
├── test_rate_limit.py              # Controlled rate limit testing
├── test_max_throughput.py          # Throughput testing with fingerprinting
├── monitor_max_speed.py            # Real-world speed monitoring
├── fingerprint.py                  # Browser fingerprinting utilities (reference)
└── README.md                       # This file
```

### Key Classes

- **TargetStockMonitor**: Main monitoring class for checking stock and pricing
- **BrowserFingerprint**: Generates realistic browser headers (User-Agent, Accept-Language, etc.)
- **MaxThroughputTester**: Tests API throughput with fingerprinting and visitor ID rotation

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

## Browser & TLS Fingerprinting & Anti-Bot Evasion

### Overview

The `test_max_throughput.py` script includes advanced multi-layer fingerprinting to evade Target's anti-bot detection:

1. **HTTP Browser Fingerprinting**: User-Agent, Accept-Language, DNT headers
2. **TLS Fingerprinting**: Cipher suites, supported curves, extension order (via `tls-client`)
3. **Session Management**: Visitor ID rotation to break Target's session tracking

This layered approach makes API requests appear as organic browser traffic rather than bot activity.

### Features

#### 1. **Browser Fingerprint Rotation**
Each batch of 10 requests uses a consistent browser fingerprint that includes:
- **User-Agent**: Rotates between Chrome, Firefox, Safari across Windows/macOS/Linux
- **Accept-Language**: Varies between en-US, en-GB, and other language preferences
- **Accept-Encoding**: Gzip, deflate, Brotli compression preferences
- **DNT Header**: Do Not Track flag (1 or 2)
- **Sec-Fetch-* Headers**: Browser security metadata

#### 2. **Persistent Visitor ID Rotation**
- Generates random `visitor_id` values following Target's format: `01` + 30 hex characters
- Rotates visitor_id every 10 requests (matches fingerprint rotation)
- Breaks Target's session tracking by appearing as different users/devices
- Prevents IP-based rate limiting by simulating organic traffic patterns

#### 3. **TLS Fingerprinting (Advanced)**
Advanced TLS/SSL fingerprinting using `tls-client` library:
- **JA3 Fingerprinting**: Each browser has unique TLS fingerprint (cipher suite order, supported curves, etc.)
- **Browser-Matched Profiles**:
  - Chrome: chrome_120, chrome_117, chrome_116_PSK, chrome_112, chrome_110
  - Firefox: firefox_120, firefox_117, firefox_108
  - Safari: safari_16_0, safari_15_6_1, safari_15_3
- **Per-Batch Rotation**: TLS profile changes every 10 requests, matching new browser fingerprint
- **Randomized Extensions**: TLS extension order randomized within each profile

Why TLS matters:
- Anti-bot systems scan JA3 fingerprints (TLS handshake signatures)
- Same TLS profile from different IPs = obvious bot
- Rotating TLS profiles + browser headers = traffic looks organic
- Services like Cloudflare, Datadome block detected bots at TLS layer

#### 4. **Why This Works**

**The Problem (Old Approach):**
- Changing headers on every request = obvious bot behavior → 404 responses
- Hardcoded visitor_id = session gets throttled after ~20 requests
- Same TLS fingerprint with rotating headers = obvious bot (JA3 mismatch)
- Target detects patterns at multiple layers and blocks requests

**The Solution (Multi-Layer Approach):**
- Persistent HTTP fingerprints (10-request batches) = realistic browser headers
- Matching TLS profiles (JA3 fingerprints) = consistent with HTTP profile
- Rotating visitor_ids = appears as different users/sessions
- All layers rotate together = coordinated, organic traffic patterns
- Result: Consistent 200 responses and real rate limit testing (not anti-bot 404s)

### Implementation

#### BrowserFingerprint Class
```python
BrowserFingerprint.get_random_fingerprint()
```
Returns a dictionary of realistic browser headers.

#### TLSFingerprint Class
```python
TLSFingerprint.get_tls_profile(browser_type)
```
Returns TLS client identifier matching browser (chrome_120, firefox_120, safari_16_0, etc.)

```python
TLSFingerprint.get_browser_type_from_user_agent(user_agent)
```
Extracts browser type from User-Agent string (chrome, firefox, safari, edge)

```python
TLSFingerprint.create_tls_session(tls_profile, random_order=True)
```
Creates `tls_client.Session` with specified TLS profile and randomized extension order

#### MaxThroughputTester Methods
```python
get_persistent_fingerprint(rotate_every=10)
```
Returns `(fingerprint_headers, visitor_id, tls_profile, tls_session)` tuple with rotation every N requests.

```python
_generate_visitor_id()
```
Generates random visitor IDs in Target's format: `01` + 30 hex chars

```python
__init__(tcin, store_id, use_tls=True)
```
Initialize tester with optional TLS fingerprinting (disabled if tls-client not installed)

### Usage Example

```python
# Enable TLS fingerprinting (automatic if tls-client installed)
tester = MaxThroughputTester(tcin="92751015", store_id="3241", use_tls=True)

# Run throughput test
results = tester.test_unlimited_concurrent(
    num_requests=50,
    max_workers=10,
    request_type="stock"
)
```

Each 10-request batch uses:
- **HTTP Layer**: Same User-Agent, Accept-Language, DNT header
- **Session Layer**: Same visitor_id
- **TLS Layer**: Same cipher suites, curve order, extension set
- Then rotates all three together to new "browser session"

**Example Flow:**
```
Requests 1-10:   Chrome 120 TLS + Chrome User-Agent + visitor_id_A
Requests 11-20:  Firefox 120 TLS + Firefox User-Agent + visitor_id_B
Requests 21-30:  Safari 16.0 TLS + Safari User-Agent + visitor_id_C
Requests 31-40:  Chrome 117 TLS + Chrome User-Agent + visitor_id_D
```

This coordinated rotation across all three layers makes traffic appear as multiple real browsers rather than a single bot.

### Installation

```bash
# Install base dependencies
pip install -r requirements.txt

# This includes:
# - requests>=2.31.0    (HTTP client)
# - tls-client>=1.0.1   (TLS fingerprinting)
```

If you have an existing installation without tls-client:
```bash
pip install tls-client>=1.0.1
```

### TLS Fingerprinting (Optional)

TLS fingerprinting is **enabled by default** if `tls-client` is installed, but can be disabled:

```python
# Disable TLS fingerprinting (use HTTP fingerprinting only)
tester = MaxThroughputTester(tcin="92751015", store_id="3241", use_tls=False)
```

**Current Status:**
- ✅ HTTP fingerprinting (User-Agent, headers, visitor_id): Proven effective
- ⚠️ TLS fingerprinting (JA3 profiles, cipher suites): Experimental, results mixed (0-40% success rates)

**Recommendation:** For most use cases, disable TLS (`use_tls=False`) and rely on HTTP fingerprinting + visitor ID rotation, which consistently achieves better results. TLS fingerprinting is available for comprehensive testing but may not improve detection evasion with Target's specific anti-bot system.

## Testing Tools

Three testing scripts are included:

- `test_rate_limit.py` - Controlled rate testing (sequential, concurrent, sustained)
- `test_max_throughput.py` - Unleashed throughput testing with browser fingerprinting and anti-bot evasion
- `monitor_max_speed.py` - Real-world monitoring at maximum speed with performance tracking

### Running Tests

```bash
# Test with browser fingerprinting and visitor_id rotation
python test_max_throughput.py

# Controlled rate testing
python test_rate_limit.py

# Maximum speed monitoring
python monitor_max_speed.py
```

### test_max_throughput.py Output

The script reports:
- Browser fingerprinting status (rotation every 10 requests)
- Visitor ID regeneration with each fingerprint batch
- Per-request status codes (200, 429, 404, etc.)
- Success/failure/rate-limit rates
- Throughput metrics (requests/second)
- Scaling analysis (performance with 5, 10, 20, 30, 50 workers)

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "HTTP 404" errors in test | This indicates anti-bot detection. Use `test_max_throughput.py` which includes fingerprinting. 404s are fake blocks, not real errors. |
| "HTTP 429" error | Rate limited; increase check interval to 60+ seconds |
| "HTTP 410" error | Product may be discontinued; try a different TCIN |
| "Store not found" | Verify your store ID is correct |
| "Module not found" | Run `pip install requests` |
| Connection errors | Check internet connection and firewall settings |
| Inconsistent results | Browser fingerprinting is enabled. Each 10-request batch rotates headers and visitor_id. Inconsistency = anti-bot evasion working |
| Low success rates with TLS enabled | TLS fingerprinting is experimental. Try disabling with `use_tls=False`. HTTP fingerprinting alone is often more effective |
| "Session.execute_request() got" errors | TLS session errors; automatically falls back to `requests`. If persistent, disable TLS or check tls-client version compatibility |

### Understanding 404 Responses

In testing, 404 responses often indicate Target's anti-bot system, not actual API errors:

**Causes:**
- Same hardcoded `visitor_id` repeatedly (session gets blocked)
- Same User-Agent for 100+ requests (looks like bot)
- No variety in Accept headers or DNT values
- TLS fingerprint mismatches (with TLS fingerprinting enabled)

**Solution:**
- `test_max_throughput.py` includes automatic HTTP fingerprinting
- Visitor IDs rotate every 10 requests (breaks session tracking)
- Headers vary naturally (looks organic)
- Result: Real 200/429 responses instead of fake 404s

### Test Results & Recommendations

**What Works:**
- ✅ HTTP browser fingerprinting (User-Agent, Accept-Language, DNT)
- ✅ Visitor ID rotation (changes session every 10 requests)
- ✅ Low-frequency sustained monitoring (1-2 req/s)
- ✅ Moderate concurrency (3-5 workers)

**What's Experimental:**
- ⚠️ TLS fingerprinting (mixed results, 0-40% success in current tests)
- ⚠️ High concurrency (20+ workers often triggers additional blocking)

**Recommended Configuration:**
```python
# Best for API testing and discovering real rate limits
tester = MaxThroughputTester(tcin="92751015", store_id="3241", use_tls=False)

# For production monitoring, use target_stock_monitor.py with 60+ second intervals
# instead of running high-concurrency tests
```

The TLS fingerprinting layer is implemented for comprehensive anti-bot research but may not improve results with Target's current detection systems, which primarily focus on HTTP-level patterns and IP reputation.

## License

Personal automation tool. Use responsibly in accordance with Target's Terms of Service.
