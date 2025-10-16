"""
Max Speed Stock Monitor
Runs the stock monitor at maximum throughput without rate limiting.
Tracks performance metrics and throughput in real-time.
"""

import requests
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
from target_stock_monitor import TargetStockMonitor


class MaxSpeedMonitor:
    """Run stock monitoring at maximum speed with performance tracking."""

    def __init__(self, tcin: str = "80790841", store_id: str = "3241"):
        """Initialize the max speed monitor."""
        self.monitor = TargetStockMonitor(tcin=tcin, store_id=store_id)
        self.lock = threading.Lock()

        # Performance tracking
        self.total_requests = 0
        self.successful_checks = 0
        self.failed_checks = 0
        self.in_stock_found = False
        self.start_time = None
        self.latest_stock_info = None
        self.latest_price_info = None

        # Per-second tracking
        self.requests_this_second = 0
        self.current_second = None
        self.throughput_history = []

    def run_continuous(self, duration: int = 60, max_attempts: Optional[int] = None,
                      check_price: bool = True) -> Dict:
        """
        Run continuous monitoring at maximum speed.

        Args:
            duration: How long to run (seconds)
            max_attempts: Max number of checks (None = unlimited)
            check_price: Whether to also fetch price data

        Returns:
            Dictionary with performance statistics
        """
        print(f"\n{'=' * 70}")
        print(f"MAX SPEED STOCK MONITOR")
        print(f"  TCIN: {self.monitor.tcin}")
        print(f"  Store ID: {self.monitor.store_id}")
        print(f"  Duration: {duration}s")
        print(f"  Check Price: {check_price}")
        if max_attempts:
            print(f"  Max Attempts: {max_attempts}")
        print(f"{'=' * 70}\n")

        self.start_time = time.time()
        attempt = 0

        # Start throughput tracker thread
        tracker_thread = threading.Thread(
            target=self._track_throughput,
            daemon=True
        )
        tracker_thread.start()

        print(f"[{self._timestamp()}] Starting max speed monitor...")
        print("-" * 70)

        while True:
            # Check time limit
            if time.time() - self.start_time >= duration:
                print(f"\n[{self._timestamp()}] Duration limit reached ({duration}s)")
                break

            # Check attempt limit
            if max_attempts and attempt >= max_attempts:
                print(f"\n[{self._timestamp()}] Max attempts reached ({max_attempts})")
                break

            attempt += 1

            # Execute checks
            self._perform_check(attempt, check_price)

            # Update second counter
            with self.lock:
                self.requests_this_second += 1

            # Stop if found in stock
            if self.in_stock_found:
                break

        # Final stats
        elapsed = time.time() - self.start_time
        results = self._compile_results(elapsed)

        self._print_summary(results)

        return results

    def _perform_check(self, attempt: int, check_price: bool = True):
        """Perform a single stock check."""
        check_start = time.time()

        try:
            stock_info = self.monitor.check_stock()
            check_time = time.time() - check_start

            with self.lock:
                self.total_requests += 1
                self.requests_this_second += 1

            if stock_info:
                with self.lock:
                    self.successful_checks += 1
                    self.latest_stock_info = stock_info

                quantity = stock_info.get("quantity", 0)
                location = stock_info.get("location_name", "Unknown")

                # Check price if requested
                price_str = "N/A"
                if check_price:
                    price_info = self.monitor.get_price()
                    if price_info:
                        with self.lock:
                            self.latest_price_info = price_info
                        price_str = price_info.get("formatted_price", "N/A")

                # Check if in stock
                if quantity > 0:
                    with self.lock:
                        self.in_stock_found = True
                    print(f"\n{'=' * 70}")
                    print(f"[{self._timestamp()}] 🎯 IN STOCK! 🎯")
                    print(f"Location: {location}")
                    print(f"Quantity: {quantity}")
                    print(f"Price: {price_str}")
                    print(f"Store ID: {self.monitor.store_id}")
                    print(f"TCIN: {self.monitor.tcin}")
                    print(f"Found after {attempt} attempts in {time.time() - self.start_time:.2f}s")
                    print(f"{'=' * 70}\n")
                else:
                    status = f"Out: {location} | Price: {price_str} | {check_time:.3f}s"
                    # Only print every 10th attempt to avoid spam
                    if attempt % 10 == 0:
                        print(f"[{self._timestamp()}] Attempt {attempt}: {status}")

            else:
                with self.lock:
                    self.failed_checks += 1
                if attempt % 10 == 0:
                    print(f"[{self._timestamp()}] Attempt {attempt}: Check failed")

        except Exception as e:
            with self.lock:
                self.failed_checks += 1
            if attempt % 10 == 0:
                print(f"[{self._timestamp()}] Attempt {attempt}: Error - {str(e)[:50]}")

    def _track_throughput(self):
        """Track throughput per second in background."""
        while True:
            time.sleep(1)
            current_time = time.time()

            with self.lock:
                rps = self.requests_this_second
                self.throughput_history.append({
                    "timestamp": current_time - self.start_time,
                    "requests": rps,
                    "total_so_far": self.total_requests
                })
                self.requests_this_second = 0

    def _compile_results(self, elapsed: float) -> Dict:
        """Compile all performance metrics."""
        avg_rps = self.total_requests / elapsed if elapsed > 0 else 0

        # Calculate peak and average throughput
        if self.throughput_history:
            peak_rps = max(h["requests"] for h in self.throughput_history)
            avg_rps_per_sec = sum(h["requests"] for h in self.throughput_history) / len(self.throughput_history)
        else:
            peak_rps = avg_rps
            avg_rps_per_sec = avg_rps

        return {
            "total_time": elapsed,
            "total_requests": self.total_requests,
            "successful": self.successful_checks,
            "failed": self.failed_checks,
            "in_stock_found": self.in_stock_found,
            "avg_rps": avg_rps,
            "peak_rps": peak_rps,
            "avg_rps_per_second": avg_rps_per_sec,
            "latest_stock_info": self.latest_stock_info,
            "latest_price_info": self.latest_price_info,
            "throughput_history": self.throughput_history
        }

    def _print_summary(self, results: Dict):
        """Print comprehensive summary."""
        print(f"\n{'=' * 70}")
        print("PERFORMANCE SUMMARY")
        print(f"{'=' * 70}")

        print(f"\nTiming:")
        print(f"  Duration: {results['total_time']:.2f}s")

        print(f"\nRequests:")
        print(f"  Total Requests: {results['total_requests']}")
        print(f"  Successful: {results['successful']} ({100*results['successful']/max(1, results['total_requests']):.1f}%)")
        print(f"  Failed: {results['failed']} ({100*results['failed']/max(1, results['total_requests']):.1f}%)")

        print(f"\nThroughput:")
        print(f"  Average: {results['avg_rps']:.2f} req/s")
        print(f"  Peak: {results['peak_rps']} req/s")
        print(f"  Per-Second Avg: {results['avg_rps_per_second']:.2f} req/s")

        print(f"\nResult:")
        if results['in_stock_found']:
            print(f"  ✓ IN STOCK FOUND!")
            if results['latest_stock_info']:
                print(f"    Location: {results['latest_stock_info'].get('location_name')}")
                print(f"    Quantity: {results['latest_stock_info'].get('quantity')}")
            if results['latest_price_info']:
                print(f"    Price: {results['latest_price_info'].get('formatted_price')}")
        else:
            print(f"  ✗ Item not found in stock")

        print(f"\nThroughput Over Time (last 10 seconds):")
        if results['throughput_history']:
            recent = results['throughput_history'][-10:]
            for h in recent:
                bar_length = int(h['requests'] / 2)  # Scale for display
                bar = "█" * bar_length
                print(f"  {h['timestamp']:6.1f}s: {bar} {h['requests']} req/s")

        print(f"{'=' * 70}\n")

    @staticmethod
    def _timestamp() -> str:
        """Return formatted timestamp."""
        return datetime.now().strftime("%H:%M:%S")


def main():
    """Run max speed monitoring."""
    monitor = MaxSpeedMonitor(tcin="80790841", store_id="3241")

    print("\n" + "=" * 70)
    print("UNLEASHED STOCK MONITOR - MAXIMUM SPEED")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Run at max speed for 60 seconds
    results = monitor.run_continuous(
        duration=60,  # Run for 60 seconds
        max_attempts=None,  # No attempt limit
        check_price=True  # Also fetch prices
    )

    # Print detailed throughput breakdown
    if results['throughput_history']:
        print("\nDetailed Throughput Breakdown (all seconds):")
        print(f"{'Second':<8} {'Requests':<12} {'Total So Far':<15}")
        print("-" * 70)
        for h in results['throughput_history']:
            print(f"{h['timestamp']:6.1f}s: {h['requests']:10} req {h['total_so_far']:14} total")


if __name__ == "__main__":
    main()
