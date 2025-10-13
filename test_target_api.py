#!/usr/bin/env python3
"""
Test script to validate the Target API connection and response parsing.
"""

from target_stock_monitor import TargetStockMonitor
import json


def test_single_check():
    """Perform a single stock check and display the results."""

    # Configuration
    TCIN = "80790841"
    STORE_ID = "3241"

    print("=" * 60)
    print("Target API Test")
    print("=" * 60)
    print(f"Product TCIN: {TCIN}")
    print(f"Store ID: {STORE_ID}")
    print("=" * 60)
    print()

    # Initialize monitor
    monitor = TargetStockMonitor(tcin=TCIN, store_id=STORE_ID)

    # Perform single check
    print("Making API request...")
    stock_info = monitor.check_stock()

    if stock_info:
        print("\n✓ API request successful!")
        print("-" * 60)
        print(f"Location: {stock_info['location_name']}")
        print(f"Store ID: {stock_info['store_id']}")
        print(f"Quantity Available: {stock_info['quantity']}")
        print(f"In Stock: {'YES' if stock_info['in_stock'] else 'NO'}")
        print("-" * 60)
        print("\nFull stock info:")
        print(json.dumps(stock_info, indent=2))
    else:
        print("\n✗ API request failed. Check the error messages above.")


if __name__ == "__main__":
    test_single_check()
