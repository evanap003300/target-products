#!/usr/bin/env python3
"""
Debug script to investigate the Target API response in detail.
"""

import requests
import json


def debug_api_request():
    """Perform a detailed API request with full debugging output."""

    # Configuration
    BASE_URL = "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_and_variation_hierarchy_v1"
    API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"
    TCIN = "80790841"
    STORE_ID = "3241"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
    }

    params = {
        "key": API_KEY,
        "tcin": TCIN,
        "store_id": STORE_ID,
        "required_store_id": STORE_ID,
        "scheduled_delivery_store_id": STORE_ID,
        "zip": "27599",
        "state": "NC",
        "latitude": "35.930",
        "longitude": "-79.040",
        "visitor_id": "0199DAB6A80D0201856B220F9301DDE6",
        "paid_membership": "false",
        "base_membership": "false",
        "card_membership": "false",
        "is_bot": "false",
        "channel": "WEB",
        "page": f"/p/A-{TCIN}"
    }

    print("=" * 80)
    print("DEBUG: Target API Request Details")
    print("=" * 80)
    print(f"\nURL: {BASE_URL}")
    print(f"\nHeaders:")
    print(json.dumps(headers, indent=2))
    print(f"\nParameters:")
    print(json.dumps(params, indent=2))
    print("\n" + "=" * 80)
    print("Making request...")
    print("=" * 80 + "\n")

    try:
        response = requests.get(BASE_URL, params=params, headers=headers, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Reason: {response.reason}")
        print(f"\nResponse Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")

        print(f"\nResponse Body (first 2000 chars):")
        print("-" * 80)
        print(response.text[:2000])
        print("-" * 80)

        # Try to parse as JSON
        if response.headers.get('Content-Type', '').startswith('application/json'):
            try:
                data = response.json()
                print("\nParsed JSON:")
                print(json.dumps(data, indent=2)[:2000])
            except json.JSONDecodeError:
                print("\nCould not parse response as JSON")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    debug_api_request()
