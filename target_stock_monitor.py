#!/usr/bin/env python3
"""
Target Product Stock Monitor
Monitors Target product availability and alerts when in stock.
"""

import requests
import time
import json
from typing import Optional, Dict, Any
from datetime import datetime


class TargetStockMonitor:
    """Monitor Target product stock availability."""

    # API Configuration
    BASE_URL = "https://redsky.target.com/redsky_aggregations/v1/web/product_fulfillment_and_variation_hierarchy_v1"
    API_KEY = "9f36aeafbe60771e321a7cc95a78140772ab3e96"

    def __init__(self, tcin: str, store_id: str, zip_code: str = "27599",
                 state: str = "NC", latitude: str = "35.930", longitude: str = "-79.040"):
        """
        Initialize the stock monitor.

        Args:
            tcin: Target product TCIN (e.g., "94973620")
            store_id: Target store ID (e.g., "3241")
            zip_code: ZIP code for the location
            state: State abbreviation
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        """
        self.tcin = tcin
        self.store_id = store_id
        self.zip_code = zip_code
        self.state = state
        self.latitude = latitude
        self.longitude = longitude

        # Headers for the request
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
        }

        # Request parameters
        self.params = {
            "key": self.API_KEY,
            "tcin": self.tcin,
            "store_id": self.store_id,
            "required_store_id": self.store_id,
            "scheduled_delivery_store_id": self.store_id,
            "zip": self.zip_code,
            "state": self.state,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "visitor_id": "0199DAB6A80D0201856B220F9301DDE6",
            "paid_membership": "false",
            "base_membership": "false",
            "card_membership": "false",
            "is_bot": "false",
            "channel": "WEB",
            "page": f"/p/A-{self.tcin}"
        }

    def check_stock(self) -> Optional[Dict[str, Any]]:
        """
        Check the current stock status for the product.

        Returns:
            Dictionary with stock information or None if request fails
        """
        try:
            response = requests.get(
                self.BASE_URL,
                params=self.params,
                headers=self.headers,
                timeout=10
            )

            # Check for successful response
            if response.status_code == 200:
                return self._parse_response(response.json())
            elif response.status_code == 429:
                print(f"[{self._timestamp()}] Rate limited (429). Backing off...")
                return None
            elif response.status_code == 403:
                print(f"[{self._timestamp()}] Access forbidden (403). Headers may need updating.")
                return None
            elif response.status_code == 503:
                print(f"[{self._timestamp()}] Service unavailable (503). Target servers may be down.")
                return None
            else:
                print(f"[{self._timestamp()}] HTTP {response.status_code}: {response.reason}")
                return None

        except requests.exceptions.Timeout:
            print(f"[{self._timestamp()}] Request timed out. Retrying later...")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[{self._timestamp()}] Connection error. Check your internet connection.")
            return None
        except requests.exceptions.RequestException as e:
            print(f"[{self._timestamp()}] Request error: {e}")
            return None
        except Exception as e:
            print(f"[{self._timestamp()}] Unexpected error: {e}")
            return None

    def _parse_response(self, data: Dict) -> Optional[Dict[str, Any]]:
        """
        Parse the API response to extract stock information.

        Args:
            data: JSON response from the API

        Returns:
            Dictionary with parsed stock data or None if parsing fails
        """
        try:
            # Navigate to the store options
            fulfillment = data.get("data", {}).get("product", {}).get("fulfillment", {})
            store_options = fulfillment.get("store_options", [])

            # Find the matching store
            for store in store_options:
                # location_id can be string or int, normalize to string for comparison
                location_id = str(store.get("location_id", ""))

                if location_id == self.store_id:
                    quantity = store.get("location_available_to_promise_quantity", 0)
                    # Store info is nested in the 'store' object
                    store_info = store.get("store", {})
                    location_name = store_info.get("location_name", "Unknown Store")

                    return {
                        "quantity": quantity,
                        "location_name": location_name,
                        "store_id": self.store_id,
                        "in_stock": quantity > 0
                    }

            # Store not found in options
            print(f"[{self._timestamp()}] Store {self.store_id} not found in response.")
            return None

        except (KeyError, AttributeError, TypeError) as e:
            print(f"[{self._timestamp()}] Error parsing response: {e}")
            return None

    def monitor(self, check_interval: int = 60, max_attempts: Optional[int] = None):
        """
        Continuously monitor stock until product is available.

        Args:
            check_interval: Seconds between checks (default: 60)
            max_attempts: Maximum number of attempts (None for unlimited)
        """
        attempt = 0
        print(f"[{self._timestamp()}] Starting stock monitor for TCIN: {self.tcin}")
        print(f"[{self._timestamp()}] Checking store: {self.store_id}")
        print(f"[{self._timestamp()}] Check interval: {check_interval} seconds")
        print("-" * 60)

        while True:
            attempt += 1

            if max_attempts and attempt > max_attempts:
                print(f"\n[{self._timestamp()}] Reached maximum attempts ({max_attempts}). Stopping.")
                break

            print(f"[{self._timestamp()}] Attempt #{attempt}: Checking stock...")

            stock_info = self.check_stock()

            if stock_info:
                quantity = stock_info["quantity"]
                location = stock_info["location_name"]

                if stock_info["in_stock"]:
                    print(f"\n{'=' * 60}")
                    print(f"[{self._timestamp()}] 🎯 IN STOCK! 🎯")
                    print(f"Location: {location}")
                    print(f"Quantity: {quantity}")
                    print(f"Store ID: {self.store_id}")
                    print(f"TCIN: {self.tcin}")
                    print(f"{'=' * 60}\n")
                    break
                else:
                    print(f"[{self._timestamp()}] Out of stock at {location}. Waiting {check_interval}s...")
            else:
                print(f"[{self._timestamp()}] Check failed. Waiting {check_interval}s...")

            # Wait before next check
            time.sleep(check_interval)

    @staticmethod
    def _timestamp() -> str:
        """Return formatted timestamp for logging."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point for the stock monitor."""

    # Configuration - Modify these values to monitor different products/stores
    TCIN = "87576259"  # Product TCIN
    STORE_ID = "3241"  # UNC Franklin St.
    CHECK_INTERVAL = 60  # Seconds between checks (60s = 1 minute)

    # Optional: ZIP and location for the store
    ZIP_CODE = "27599"
    STATE = "NC"
    LATITUDE = "35.930"
    LONGITUDE = "-79.040"

    # Initialize and start monitoring
    monitor = TargetStockMonitor(
        tcin=TCIN,
        store_id=STORE_ID,
        zip_code=ZIP_CODE,
        state=STATE,
        latitude=LATITUDE,
        longitude=LONGITUDE
    )

    try:
        monitor.monitor(check_interval=CHECK_INTERVAL)
    except KeyboardInterrupt:
        print(f"\n[{monitor._timestamp()}] Monitor stopped by user.")
    except Exception as e:
        print(f"\n[{monitor._timestamp()}] Fatal error: {e}")


if __name__ == "__main__":
    main()
