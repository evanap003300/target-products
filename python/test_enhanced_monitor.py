#!/usr/bin/env python3
"""
Test script for the enhanced Target Stock Monitor with pricing
"""

from target_stock_monitor import TargetStockMonitor

# Configuration
TCIN = "80790841"  # Xbox Series X Console
STORE_ID = "3241"  # UNC Franklin St.
ZIP_CODE = "27599"
STATE = "NC"
LATITUDE = "35.930"
LONGITUDE = "-79.040"

print("=" * 80)
print("Testing Enhanced Target Stock Monitor with Pricing")
print("=" * 80)
print(f"\nProduct TCIN: {TCIN}")
print(f"Store ID: {STORE_ID}")
print("-" * 80)

# Initialize the monitor
monitor = TargetStockMonitor(
    tcin=TCIN,
    store_id=STORE_ID,
    zip_code=ZIP_CODE,
    state=STATE,
    latitude=LATITUDE,
    longitude=LONGITUDE
)

# Test stock check
print("\n1. Testing Stock Check:")
print("-" * 40)
stock_info = monitor.check_stock()

if stock_info:
    print(f"✓ Stock check successful!")
    print(f"  Location: {stock_info['location_name']}")
    print(f"  Store ID: {stock_info['store_id']}")
    print(f"  Quantity: {stock_info['quantity']}")
    print(f"  In Stock: {stock_info['in_stock']}")
else:
    print("✗ Stock check failed")

# Test price check
print("\n2. Testing Price Check:")
print("-" * 40)
price_info = monitor.get_price()

if price_info:
    print(f"✓ Price check successful!")
    print(f"  Product: {price_info['title']}")
    print(f"  Price: {price_info['formatted_price']}")
    print(f"  Price (raw): ${price_info['current_retail']:.2f}")
else:
    print("✗ Price check failed")

# Display combined results
print("\n" + "=" * 80)
print("COMBINED RESULTS")
print("=" * 80)

if stock_info and price_info:
    print(f"Product: {price_info['title']}")
    print(f"Price: {price_info['formatted_price']}")
    print(f"Stock: {stock_info['quantity']} units at {stock_info['location_name']}")
    print(f"Status: {'IN STOCK' if stock_info['in_stock'] else 'OUT OF STOCK'}")
    print("=" * 80)
    print("\n✓ All tests passed! The enhanced monitor is working correctly.")
else:
    print("✗ Some checks failed. Review the output above.")

print("\n" + "=" * 80)
