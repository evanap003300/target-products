"""
Maximum Throughput Test
Tests the absolute maximum request rate without any delays or limitations.
Useful for understanding where rate limits kick in.
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List
from datetime import datetime
from target_stock_monitor import TargetStockMonitor


class MaxThroughputTester:
    """Test maximum throughput and identify rate limit thresholds."""

    def __init__(self, tcin: str = "80790841", store_id: str = "3241"):
        """Initialize the max throughput tester."""
        self.monitor = TargetStockMonitor(tcin=tcin, store_id=store_id)
        self.lock = threading.Lock()

    def test_unlimited_concurrent(self, num_requests: int = 50, max_workers: int = 10,
                                  request_type: str = "stock") -> Dict:
        """
        Send requests as fast as possible with no delays.

        Args:
            num_requests: Total number of requests to send
            max_workers: Number of parallel threads (unlimited speed)
            request_type: "stock" or "price"

        Returns:
            Dictionary with results including rate limit detection
        """
        print(f"\n{'=' * 70}")
        print(f"MAXIMUM THROUGHPUT TEST - {request_type.upper()}")
        print(f"  Total Requests: {num_requests}")
        print(f"  Parallel Threads: {max_workers}")
        print(f"  Speed: UNLIMITED (as fast as possible)")
        print(f"{'=' * 70}\n")

        start_time = time.time()
        response_times = []
        status_codes = {}
        rate_limited_count = 0
        successful = 0
        failed = 0
        completed = 0

        def make_request(request_num):
            nonlocal completed, successful, failed, rate_limited_count
            req_start = time.time()

            try:
                if request_type == "stock":
                    # Make direct request to capture status code
                    response = requests.get(
                        self.monitor.BASE_URL,
                        params=self.monitor.params,
                        headers=self.monitor.headers,
                        timeout=10
                    )
                else:
                    price_params = {
                        "key": self.monitor.API_KEY,
                        "tcin": self.monitor.tcin,
                        "pricing_store_id": self.monitor.store_id,
                    }
                    response = requests.get(
                        self.monitor.PRICE_URL,
                        params=price_params,
                        headers=self.monitor.headers,
                        timeout=10
                    )

                req_time = time.time() - req_start
                status_code = response.status_code

                with self.lock:
                    response_times.append(req_time)
                    status_codes[status_code] = status_codes.get(status_code, 0) + 1
                    completed += 1

                    if status_code == 200:
                        successful += 1
                        status = "✓ 200"
                    elif status_code == 429:
                        rate_limited_count += 1
                        status = "⚠ 429 (Rate Limited)"
                    elif status_code == 403:
                        failed += 1
                        status = "✗ 403 (Forbidden)"
                    elif status_code == 503:
                        failed += 1
                        status = "✗ 503 (Service Unavailable)"
                    else:
                        failed += 1
                        status = f"✗ {status_code}"

                    print(f"[{completed:3d}/{num_requests}] {status:30} - {req_time:.3f}s")

            except Exception as e:
                req_time = time.time() - req_start
                with self.lock:
                    response_times.append(req_time)
                    failed += 1
                    completed += 1
                    print(f"[{completed:3d}/{num_requests}] ✗ Error - {str(e)[:30]}")

        # Fire off all requests as fast as possible
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Executor error: {e}")

        total_time = time.time() - start_time
        avg_time = sum(response_times) / len(response_times) if response_times else 0

        results = {
            "type": "unlimited_concurrent",
            "endpoint": request_type,
            "total_requests": num_requests,
            "parallel_threads": max_workers,
            "total_time": total_time,
            "successful": successful,
            "rate_limited": rate_limited_count,
            "failed": failed,
            "avg_response_time": avg_time,
            "throughput_rps": num_requests / total_time if total_time > 0 else 0,
            "status_codes": status_codes
        }

        # Summary
        print(f"\n{'=' * 70}")
        print("RESULTS:")
        print(f"{'=' * 70}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {results['throughput_rps']:.2f} req/s")
        print(f"\nRequests:")
        print(f"  Successful (200):     {successful}/{num_requests} ({100*successful/num_requests:.1f}%)")
        print(f"  Rate Limited (429):   {rate_limited_count}/{num_requests} ({100*rate_limited_count/num_requests:.1f}%)")
        print(f"  Failed (other):       {failed}/{num_requests} ({100*failed/num_requests:.1f}%)")
        print(f"\nResponse Times:")
        print(f"  Avg: {avg_time:.3f}s")
        if response_times:
            print(f"  Min: {min(response_times):.3f}s")
            print(f"  Max: {max(response_times):.3f}s")
        print(f"\nStatus Codes:")
        for code, count in sorted(status_codes.items()):
            print(f"  {code}: {count}")
        print(f"{'=' * 70}\n")

        return results

    def test_scaling_workers(self, base_requests: int = 100, request_type: str = "stock") -> List[Dict]:
        """
        Test with increasing worker counts to find optimal throughput.

        Args:
            base_requests: Requests per worker count
            request_type: "stock" or "price"

        Returns:
            List of results for each worker count
        """
        results_list = []
        worker_counts = [5, 10, 20, 30, 50]

        print(f"\n{'=' * 70}")
        print(f"SCALING TEST - Finding Optimal Throughput")
        print(f"  Base Requests per Test: {base_requests}")
        print(f"  Testing Worker Counts: {worker_counts}")
        print(f"{'=' * 70}\n")

        for workers in worker_counts:
            num_requests = base_requests
            result = self.test_unlimited_concurrent(
                num_requests=num_requests,
                max_workers=workers,
                request_type=request_type
            )
            results_list.append(result)
            time.sleep(2)  # Brief pause between tests

        # Print scaling summary
        print(f"\n{'=' * 70}")
        print("SCALING SUMMARY:")
        print(f"{'=' * 70}")
        print(f"{'Workers':<12} {'Throughput':<15} {'Success Rate':<15} {'Rate Limited':<15}")
        print("-" * 70)
        for result in results_list:
            workers = result["parallel_threads"]
            throughput = result["throughput_rps"]
            total = result["total_requests"]
            success = result["successful"]
            rate_limited = result["rate_limited"]
            success_rate = 100 * success / total if total > 0 else 0
            rl_rate = 100 * rate_limited / total if total > 0 else 0
            print(f"{workers:<12} {throughput:<14.2f} {success_rate:<14.1f}% {rl_rate:<14.1f}%")
        print(f"{'=' * 70}\n")

        return results_list


def main():
    """Run maximum throughput tests."""
    tester = MaxThroughputTester(tcin="80790841", store_id="3241")

    print("\n" + "=" * 70)
    print("MAXIMUM THROUGHPUT ANALYSIS")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Testing to find rate limits and maximum throughput...")

    # Test 1: Blast stock requests with high concurrency
    print("\n\n[TEST 1] Maximum Stock Requests (50 requests, 10 workers)")
    results_stock = tester.test_unlimited_concurrent(
        num_requests=50,
        max_workers=10,
        request_type="stock"
    )

    # Test 2: Blast price requests
    print("\n[TEST 2] Maximum Price Requests (50 requests, 10 workers)")
    results_price = tester.test_unlimited_concurrent(
        num_requests=50,
        max_workers=10,
        request_type="price"
    )

    # Test 3: Scale up to find limit
    print("\n[TEST 3] Scaling Test - Finding Optimal Worker Count")
    scaling_results = tester.test_scaling_workers(base_requests=50, request_type="stock")

    # Final Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    print(f"Stock Max Throughput:  {results_stock['throughput_rps']:.2f} req/s")
    print(f"Price Max Throughput:  {results_price['throughput_rps']:.2f} req/s")
    print(f"\nRate Limit Encountered:")
    print(f"  Stock: {results_stock['rate_limited']} rate limited responses")
    print(f"  Price: {results_price['rate_limited']} rate limited responses")
    print(f"\nRecommendation:")
    if results_stock['rate_limited'] > 0 or results_price['rate_limited'] > 0:
        print(f"  Rate limits detected. Use 1-2 req/s for sustained monitoring.")
    else:
        print(f"  No rate limits detected at current test levels.")
    print("=" * 70)


if __name__ == "__main__":
    main()
