#!/usr/bin/env python3
"""
Test script to investigate Target pricing API endpoints
"""

import requests
import json

# Configuration
TCIN = "80790841"  # Xbox Series X
STORE_ID = "3241"
API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

# Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

# Test endpoints
endpoints = [
    {
        "name": "existing_fulfillment_endpoint",
        "url": "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_and_variation_hierarchy_v1",
        "params": {
            "key": API_KEY,
            "tcin": TCIN,
            "store_id": STORE_ID,
            "zip": "27599",
            "state": "NC",
            "latitude": "35.930",
            "longitude": "-79.040",
        }
    },
    {
        "name": "plp_price_promo_v1",
        "url": "https://redsky.target.com/redsky_aggregations/v1/web/plp_price_promo_v1",
        "params": {
            "key": API_KEY,
            "tcins": TCIN,  # Changed to tcins (plural)
            "store_id": STORE_ID,
            "pricing_store_id": STORE_ID,
        }
    },
    {
        "name": "product_summary_basics_v1",
        "url": "https://redsky.target.com/redsky_aggregations/v1/web/product_summary_basics_v1",
        "params": {
            "key": API_KEY,
            "tcin": TCIN,
            "pricing_store_id": STORE_ID,  # Added required param
        }
    },
    {
        "name": "product_summary_with_fulfillment_v1",
        "url": "https://redsky.target.com/redsky_aggregations/v1/web/product_summary_with_fulfillment_v1",
        "params": {
            "key": API_KEY,
            "tcins": TCIN,  # Changed to tcins (plural)
            "store_id": STORE_ID,
        }
    }
]

print("=" * 80)
print(f"Testing Target Pricing API Endpoints for TCIN: {TCIN}")
print("=" * 80)

for endpoint in endpoints:
    print(f"\n{'=' * 80}")
    print(f"Testing: {endpoint['name']}")
    print(f"URL: {endpoint['url']}")
    print(f"Params: {endpoint['params']}")
    print("-" * 80)

    try:
        response = requests.get(
            endpoint['url'],
            params=endpoint['params'],
            headers=headers,
            timeout=10
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Save full response for analysis
            output_file = f"response_{endpoint['name']}.json"
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✓ Success! Full response saved to: {output_file}")

            # Try to find price data in the response
            print("\nSearching for price data...")
            json_str = json.dumps(data)

            # Look for common price-related keys
            price_keywords = ['price', 'current_retail', 'formatted_price', 'retail', 'cost']
            found_keywords = [kw for kw in price_keywords if kw in json_str.lower()]

            if found_keywords:
                print(f"✓ Found potential price fields: {', '.join(found_keywords)}")
            else:
                print("✗ No obvious price fields found")

        else:
            print(f"✗ Failed: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 80)
print("Testing complete!")
print("=" * 80)
