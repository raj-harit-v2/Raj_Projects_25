"""
Master Test Runner for Phase 1 & 2
Executes all test suites and generates comprehensive report
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_test_file(test_file):
    """Run a single test file and return results"""
    print(f"\n{'='*60}")
    print(f"  Running: {test_file}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(result.stdout)
        if result.stderr and "Traceback" in result.stderr:
            print(f"STDERR: {result.stderr}")
        
        return {
            "file": test_file.name,
            "passed": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Test {test_file.name} exceeded 60 seconds")
        return {
            "file": test_file.name,
            "passed": False,
            "output": "",
            "errors": "Timeout"
        }
    except Exception as e:
        print(f"[ERROR] Failed to run {test_file.name}: {e}")
        return {
            "file": test_file.name,
            "passed": False,
            "output": "",
            "errors": str(e)
        }


def generate_test_report(results):
    """Generate comprehensive test report"""
    report_path = Path(__file__).parent.parent / "TEST_EXECUTION_REPORT.md"
    
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    
    report = f"""# Test Execution Report - Phase 1 & 2

## Overview
**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Total Tests:** {len(results)}  
**Passed:** {passed}  
**Failed:** {failed}  
**Success Rate:** {(passed/len(results)*100):.1f}%

---

## Test Results Summary

"""
    
    for result in results:
        status = "✅ PASSED" if result["passed"] else "❌ FAILED"
        report += f"### {result['file']}: {status}\n\n"
        
        if result["passed"]:
            # Extract key info from output
            output_lines = result["output"].split('\n')
            success_lines = [line for line in output_lines if 'SUCCESS' in line or 'PASS' in line]
            if success_lines:
                report += "```\n"
                report += "\n".join(success_lines[-5:])
                report += "\n```\n\n"
        else:
            report += "**Error:**\n```\n"
            report += result["errors"][:500]
            report += "\n```\n\n"
    
    # Overall status
    report += "\n---\n\n"
    if failed == 0:
        report += "## 🎉 ALL TESTS PASSED!\n\n"
        report += "**Status:** ✅ System fully operational  \n"
        report += "**Next Step:** Start live testing with `python agent.py`\n"
    else:
        report += f"## ⚠️ {failed} Test(s) Failed\n\n"
        report += "**Action Required:** Review failed tests and fix issues\n"
    
    report += f"\n---\n\n**Report Generated:** {datetime.now().isoformat()}  \n"
    report += f"**Test Suite:** Phase 1 & 2 Validation  \n"
    
    # Save report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[REPORT] Saved to: {report_path}")
    return report_path


def main():
    """Main test runner"""
    print("\n" + "="*70)
    print("  MASTER TEST SUITE - PHASE 1 & 2 VALIDATION")
    print("="*70)
    
    test_dir = Path(__file__).parent
    
    # Find all test files
    test_files = [
        test_dir / "test_heuristics.py",
        test_dir / "test_historical_context.py",
        test_dir / "test_integration.py"
    ]
    
    # Filter existing files
    test_files = [f for f in test_files if f.exists()]
    
    print(f"\nFound {len(test_files)} test files:")
    for tf in test_files:
        print(f"  - {tf.name}")
    
    if not test_files:
        print("\n[ERROR] No test files found!")
        return False
    
    # Run all tests
    results = []
    for test_file in test_files:
        result = run_test_file(test_file)
        results.append(result)
    
    # Generate report
    print("\n" + "="*70)
    print("  GENERATING TEST REPORT")
    print("="*70)
    
    report_path = generate_test_report(results)
    
    # Summary
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    
    print("\n" + "="*70)
    if failed == 0:
        print("  [SUCCESS] ALL TESTS PASSED!")
        print(f"  {passed}/{len(results)} test suites successful")
        print("  Status: READY FOR LIVE TESTING")
    else:
        print(f"  [WARNING] {failed}/{len(results)} test suite(s) failed")
        print("  Status: REVIEW REQUIRED")
    print("="*70 + "\n")
    
    print(f"Full report: {report_path}\n")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

