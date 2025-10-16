"""
Rate Limit Test
Tests how many requests per second can be sent to Target's API endpoints.
"""

import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from datetime import datetime
from target_stock_monitor import TargetStockMonitor


class RateLimitTester:
    """Test request rate limits for Target API endpoints."""

    def __init__(self, tcin: str = "80790841", store_id: str = "3241"):
        """Initialize the rate limit tester."""
        self.monitor = TargetStockMonitor(tcin=tcin, store_id=store_id)
        self.results = {
            "stock": {"success": 0, "failed": 0, "rate_limited": 0},
            "price": {"success": 0, "failed": 0, "rate_limited": 0}
        }

    def test_sequential(self, num_requests: int = 10, request_type: str = "stock") -> Dict:
        """
        Test requests sent sequentially (one after another).

        Args:
            num_requests: Number of requests to send
            request_type: "stock" or "price"

        Returns:
            Dictionary with timing and success information
        """
        print(f"\n{'=' * 60}")
        print(f"Sequential {request_type.upper()} Requests Test: {num_requests} requests")
        print(f"{'=' * 60}")

        start_time = time.time()
        response_times = []
        status_codes = {}

        for i in range(num_requests):
            req_start = time.time()

            if request_type == "stock":
                result = self.monitor.check_stock()
            else:
                result = self.monitor.get_price()

            req_time = time.time() - req_start
            response_times.append(req_time)

            # Track status (would need to modify monitor to return status codes)
            status = "✓ Success" if result else "✗ Failed"
            print(f"[{i+1:3d}] {status:12} - {req_time:.3f}s")

        total_time = time.time() - start_time
        avg_time = sum(response_times) / len(response_times)

        results = {
            "type": "sequential",
            "endpoint": request_type,
            "total_requests": num_requests,
            "total_time": total_time,
            "avg_response_time": avg_time,
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "requests_per_second": num_requests / total_time
        }

        print(f"\nResults:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Avg Response: {avg_time:.3f}s")
        print(f"  Min/Max: {min(response_times):.3f}s / {max(response_times):.3f}s")
        print(f"  Requests/Second: {results['requests_per_second']:.2f} req/s")

        return results

    def test_concurrent(self, num_requests: int = 10, max_workers: int = 5,
                       request_type: str = "stock") -> Dict:
        """
        Test requests sent concurrently (in parallel).

        Args:
            num_requests: Number of requests to send
            max_workers: Number of parallel threads
            request_type: "stock" or "price"

        Returns:
            Dictionary with timing and success information
        """
        print(f"\n{'=' * 60}")
        print(f"Concurrent {request_type.upper()} Requests Test")
        print(f"  Total Requests: {num_requests}")
        print(f"  Parallel Threads: {max_workers}")
        print(f"{'=' * 60}")

        start_time = time.time()
        response_times = []
        successful = 0
        failed = 0

        def make_request():
            req_start = time.time()
            try:
                if request_type == "stock":
                    result = self.monitor.check_stock()
                else:
                    result = self.monitor.get_price()
                req_time = time.time() - req_start
                return req_time, result is not None
            except Exception as e:
                req_time = time.time() - req_start
                return req_time, False

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]

            for i, future in enumerate(as_completed(futures), 1):
                try:
                    req_time, success = future.result()
                    response_times.append(req_time)
                    if success:
                        successful += 1
                        status = "✓"
                    else:
                        failed += 1
                        status = "✗"
                    print(f"[{i:3d}] {status} - {req_time:.3f}s")
                except Exception as e:
                    print(f"[{i:3d}] ✗ Error - {str(e)}")
                    failed += 1

        total_time = time.time() - start_time
        avg_time = sum(response_times) / len(response_times) if response_times else 0

        results = {
            "type": "concurrent",
            "endpoint": request_type,
            "total_requests": num_requests,
            "parallel_threads": max_workers,
            "successful": successful,
            "failed": failed,
            "total_time": total_time,
            "avg_response_time": avg_time,
            "min_response_time": min(response_times) if response_times else 0,
            "max_response_time": max(response_times) if response_times else 0,
            "requests_per_second": num_requests / total_time if total_time > 0 else 0
        }

        print(f"\nResults:")
        print(f"  Successful: {successful}/{num_requests}")
        print(f"  Failed: {failed}/{num_requests}")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Avg Response: {avg_time:.3f}s")
        if response_times:
            print(f"  Min/Max: {min(response_times):.3f}s / {max(response_times):.3f}s")
        print(f"  Requests/Second: {results['requests_per_second']:.2f} req/s")

        return results

    def test_sustained(self, requests_per_second: int = 2, duration: int = 10,
                      request_type: str = "stock") -> Dict:
        """
        Test sustained request rate over a period of time.

        Args:
            requests_per_second: Target RPS
            duration: How long to run test (seconds)
            request_type: "stock" or "price"

        Returns:
            Dictionary with timing and success information
        """
        print(f"\n{'=' * 60}")
        print(f"Sustained {request_type.upper()} Requests Test")
        print(f"  Target Rate: {requests_per_second} req/s")
        print(f"  Duration: {duration}s")
        print(f"{'=' * 60}")

        start_time = time.time()
        request_count = 0
        successful = 0
        failed = 0
        response_times = []
        rate_limited = 0

        interval = 1.0 / requests_per_second  # Time between requests

        while time.time() - start_time < duration:
            req_start = time.time()

            try:
                if request_type == "stock":
                    result = self.monitor.check_stock()
                else:
                    result = self.monitor.get_price()

                req_time = time.time() - req_start
                response_times.append(req_time)
                request_count += 1

                if result:
                    successful += 1
                    status = "✓"
                else:
                    failed += 1
                    status = "✗"
            except Exception as e:
                req_time = time.time() - req_start
                response_times.append(req_time)
                failed += 1
                status = "✗"

            elapsed = time.time() - req_start
            time_to_wait = max(0, interval - elapsed)

            print(f"[{request_count:3d}] {status} - {req_time:.3f}s (waiting {time_to_wait:.3f}s)")

            time.sleep(time_to_wait)

        total_time = time.time() - start_time
        actual_rps = request_count / total_time if total_time > 0 else 0

        results = {
            "type": "sustained",
            "endpoint": request_type,
            "target_rps": requests_per_second,
            "actual_rps": actual_rps,
            "duration": duration,
            "total_requests": request_count,
            "successful": successful,
            "failed": failed,
            "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
        }

        print(f"\nResults:")
        print(f"  Target Rate: {requests_per_second} req/s")
        print(f"  Actual Rate: {actual_rps:.2f} req/s")
        print(f"  Total Requests: {request_count}")
        print(f"  Successful: {successful}/{request_count}")
        print(f"  Failed: {failed}/{request_count}")

        return results


def main():
    """Run rate limit tests."""
    tester = RateLimitTester(tcin="80790841", store_id="3241")

    print("\n" + "=" * 60)
    print("TARGET API RATE LIMIT TEST")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test 1: Sequential stock requests
    print("\n\n[TEST 1] Sequential Stock Requests (baseline)")
    results_seq_stock = tester.test_sequential(num_requests=5, request_type="stock")

    # Test 2: Sequential price requests
    print("\n\n[TEST 2] Sequential Price Requests (baseline)")
    results_seq_price = tester.test_sequential(num_requests=5, request_type="price")

    # Test 3: Concurrent stock requests
    print("\n\n[TEST 3] Concurrent Stock Requests (3 parallel)")
    results_con_stock = tester.test_concurrent(
        num_requests=10,
        max_workers=3,
        request_type="stock"
    )

    # Test 4: Concurrent price requests
    print("\n\n[TEST 4] Concurrent Price Requests (3 parallel)")
    results_con_price = tester.test_concurrent(
        num_requests=10,
        max_workers=3,
        request_type="price"
    )

    # Test 5: Sustained rate test
    print("\n\n[TEST 5] Sustained Stock Requests (2 req/s for 30s)")
    results_sustained = tester.test_sustained(
        requests_per_second=2,
        duration=30,
        request_type="stock"
    )

    # Summary
    print("\n\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Sequential Stock:      {results_seq_stock['requests_per_second']:.2f} req/s")
    print(f"Sequential Price:      {results_seq_price['requests_per_second']:.2f} req/s")
    print(f"Concurrent Stock (3x): {results_con_stock['requests_per_second']:.2f} req/s")
    print(f"Concurrent Price (3x): {results_con_price['requests_per_second']:.2f} req/s")
    print(f"Sustained (2 req/s):   {results_sustained['actual_rps']:.2f} req/s")
    print("=" * 60)


if __name__ == "__main__":
    main()
