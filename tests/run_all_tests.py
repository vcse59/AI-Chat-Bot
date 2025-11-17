"""
Comprehensive Test Runner for AI Chat Bot

Runs all test suites in order and generates a detailed report.
"""

import sys
import time
import subprocess
from datetime import datetime


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80 + "\n")


def run_test_suite(test_file, description):
    """Run a single test suite and return results"""
    print(f"\nRunning: {description}")
    print(f"File: {test_file}")
    print("-" * 80)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            ["pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout per suite
        )
        
        elapsed = time.time() - start_time
        
        # Parse output
        passed = result.stdout.count(" PASSED")
        failed = result.stdout.count(" FAILED")
        skipped = result.stdout.count(" SKIPPED")
        errors = result.stdout.count(" ERROR")
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return {
            "file": test_file,
            "description": description,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "errors": errors,
            "duration": elapsed,
            "success": result.returncode == 0
        }
    
    except subprocess.TimeoutExpired:
        print(f"❌ Test suite timed out after 5 minutes")
        return {
            "file": test_file,
            "description": description,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 1,
            "duration": 300,
            "success": False
        }
    
    except Exception as e:
        print(f"❌ Error running test suite: {e}")
        return {
            "file": test_file,
            "description": description,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 1,
            "duration": 0,
            "success": False
        }


def main():
    """Main test runner"""
    print_header("AI Chat Bot - Comprehensive Test Suite")
    print(f"Test Run Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define test suites in execution order
    test_suites = [
        ("test_0_smoke.py", "Smoke Tests - Service Availability"),
        ("test_1_auth_service.py", "Authentication & Authorization Service"),
        ("test_2_chat_api.py", "Chat API & Conversation Management"),
        ("test_3_websocket.py", "WebSocket Real-time Communication"),
        ("test_4_end_to_end.py", "End-to-End Integration Tests"),
        ("test_5_analytics.py", "Analytics Service & Dashboard"),
        ("test_6_admin_features.py", "Admin Features & Permissions"),
        ("test_7_database_integrity.py", "Database Integrity & Data Isolation"),
    ]
    
    results = []
    total_start = time.time()
    
    # Run each test suite
    for test_file, description in test_suites:
        result = run_test_suite(test_file, description)
        results.append(result)
        
        if not result["success"]:
            print(f"\n⚠️  Test suite failed: {description}")
            if "--fail-fast" in sys.argv:
                print("\n🛑 Stopping test run due to --fail-fast flag")
                break
    
    total_duration = time.time() - total_start
    
    # Print summary
    print_header("Test Run Summary")
    
    total_passed = sum(r["passed"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    total_skipped = sum(r["skipped"] for r in results)
    total_errors = sum(r["errors"] for r in results)
    suites_passed = sum(1 for r in results if r["success"])
    suites_failed = len(results) - suites_passed
    
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"\nTest Suites: {len(results)} total")
    print(f"  ✅ Passed: {suites_passed}")
    print(f"  ❌ Failed: {suites_failed}")
    
    print(f"\nTest Cases:")
    print(f"  ✅ Passed: {total_passed}")
    print(f"  ❌ Failed: {total_failed}")
    print(f"  ⏭️  Skipped: {total_skipped}")
    print(f"  ❌ Errors: {total_errors}")
    
    print("\n" + "-" * 80)
    print("Detailed Results by Suite:")
    print("-" * 80)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"\n{status} | {result['description']}")
        print(f"  File: {result['file']}")
        print(f"  Duration: {result['duration']:.2f}s")
        print(f"  Passed: {result['passed']}, Failed: {result['failed']}, "
              f"Skipped: {result['skipped']}, Errors: {result['errors']}")
    
    # Generate report file
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, "w") as f:
        f.write("AI Chat Bot - Test Report\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Duration: {total_duration:.2f} seconds\n")
        f.write(f"\nTest Suites: {suites_passed}/{len(results)} passed\n")
        f.write(f"Test Cases: {total_passed} passed, {total_failed} failed, "
                f"{total_skipped} skipped, {total_errors} errors\n")
        f.write("\n" + "=" * 80 + "\n")
        
        for result in results:
            status = "PASS" if result["success"] else "FAIL"
            f.write(f"\n[{status}] {result['description']}\n")
            f.write(f"  File: {result['file']}\n")
            f.write(f"  Duration: {result['duration']:.2f}s\n")
            f.write(f"  Passed: {result['passed']}, Failed: {result['failed']}, "
                   f"Skipped: {result['skipped']}, Errors: {result['errors']}\n")
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if suites_failed > 0 or total_failed > 0 or total_errors > 0:
        print("\n❌ Test run FAILED")
        sys.exit(1)
    else:
        print("\n✅ All tests PASSED")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
