"""
MASTER TEST RUNNER - Complete Security Testing Suite
Orchestrates all vulnerability tests and generates comprehensive reports
"""

import subprocess
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List
from datetime import datetime

class MasterTestRunner:
    """Orchestrates complete security testing workflow"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = workspace_root or os.getcwd()
        self.pre_mitigation_dir = os.path.join(self.workspace_root, "pre-mitigation")
        self.post_mitigation_dir = os.path.join(self.workspace_root, "post-mitigation")
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "pre_mitigation": None,
            "post_mitigation": None,
            "comparison": None
        }
    
    def run_pre_mitigation_tests(self) -> Dict:
        """Run vulnerability tests on pre-mitigation version"""
        print("\n" + "="*80)
        print("PHASE 1: TESTING VULNERABLE (PRE-MITIGATION) VERSION")
        print("="*80)
        
        try:
            # Start vulnerable app
            print("[*] Starting vulnerable Flask app on port 5000...")
            app_process = subprocess.Popen(
                [sys.executable, "app/app.py"],
                cwd=self.pre_mitigation_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for app to start
            time.sleep(3)
            
            if app_process.poll() is not None:
                print("[!] Failed to start vulnerable app")
                return None
            
            print("[+] Vulnerable app started")
            
            # Run exploit tests
            print("[*] Running exploit tests...")
            result = subprocess.run(
                [sys.executable, "tests/exploit_tests.py"],
                cwd=self.pre_mitigation_dir,
                capture_output=True,
                text=True
            )
            
            # Read results
            results_file = os.path.join(self.pre_mitigation_dir, "exploit_results.json")
            if os.path.exists(results_file):
                with open(results_file) as f:
                    results = json.load(f)
                print(f"[+] Exploit tests completed: {len(results['exploits'])} vulnerabilities found")
                return results
            else:
                print("[!] No results file generated")
                return None
        
        except Exception as e:
            print(f"[!] Error during pre-mitigation testing: {e}")
            return None
        
        finally:
            # Cleanup
            try:
                app_process.terminate()
                app_process.wait(timeout=5)
            except:
                app_process.kill()
    
    def run_post_mitigation_tests(self) -> Dict:
        """Run validation tests on post-mitigation version"""
        print("\n" + "="*80)
        print("PHASE 2: TESTING SECURE (POST-MITIGATION) VERSION")
        print("="*80)
        
        try:
            # Setup environment
            env_file = os.path.join(self.post_mitigation_dir, ".env")
            if not os.path.exists(env_file):
                print("[*] Creating .env file...")
                example_file = os.path.join(self.post_mitigation_dir, ".env.example")
                if os.path.exists(example_file):
                    with open(example_file) as src:
                        with open(env_file, 'w') as dst:
                            dst.write(src.read())
            
            # Start secure app
            print("[*] Starting secure Flask app on port 5001...")
            env = os.environ.copy()
            env['FLASK_DEBUG'] = 'False'
            env['ENVIRONMENT'] = 'production'
            
            app_process = subprocess.Popen(
                [sys.executable, "app/app.py"],
                cwd=self.post_mitigation_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Wait for app to start
            time.sleep(3)
            
            if app_process.poll() is not None:
                print("[!] Failed to start secure app")
                return None
            
            print("[+] Secure app started")
            
            # Run validation tests
            print("[*] Running security validations...")
            result = subprocess.run(
                [sys.executable, "tests/validation_tests.py"],
                cwd=self.post_mitigation_dir,
                capture_output=True,
                text=True
            )
            
            # Read results
            results_file = os.path.join(self.post_mitigation_dir, "validation_results.json")
            if os.path.exists(results_file):
                with open(results_file) as f:
                    results = json.load(f)
                passed = results['summary']['passed']
                failed = results['summary']['failed']
                print(f"[+] Validation tests completed: {passed} passed, {failed} failed")
                return results
            else:
                print("[!] No results file generated")
                return None
        
        except Exception as e:
            print(f"[!] Error during post-mitigation testing: {e}")
            return None
        
        finally:
            # Cleanup
            try:
                app_process.terminate()
                app_process.wait(timeout=5)
            except:
                app_process.kill()
    
    def generate_comparison_report(self) -> Dict:
        """Generate comparison between vulnerable and secure versions"""
        print("\n" + "="*80)
        print("GENERATING COMPARISON REPORT")
        print("="*80)
        
        comparison = {
            "pre_mitigation_vulnerabilities": len(self.results.get("pre_mitigation", {}).get("exploits", [])),
            "post_mitigation_validations_passed": self.results.get("post_mitigation", {}).get("summary", {}).get("passed", 0),
            "post_mitigation_validations_failed": self.results.get("post_mitigation", {}).get("summary", {}).get("failed", 0),
        }
        
        return comparison
    
    def run_all_tests(self) -> Dict:
        """Execute complete testing workflow"""
        print("\n" + "█"*80)
        print("█ UI SECURITY VULNERABILITY TESTING SUITE")
        print("█"*80)
        
        # Phase 1: Pre-mitigation tests
        self.results["pre_mitigation"] = self.run_pre_mitigation_tests()
        
        # Phase 2: Post-mitigation tests
        self.results["post_mitigation"] = self.run_post_mitigation_tests()
        
        # Phase 3: Generate comparison
        self.results["comparison"] = self.generate_comparison_report()
        
        return self.results
    
    def save_results(self, filename: str = "test_results.json"):
        """Save all test results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"[+] Results saved to: {filename}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        if self.results.get("pre_mitigation"):
            vulns = len(self.results["pre_mitigation"].get("exploits", []))
            print(f"\n[*] Pre-Mitigation Results:")
            print(f"    - Vulnerabilities Found: {vulns}")
        
        if self.results.get("post_mitigation"):
            summary = self.results["post_mitigation"].get("summary", {})
            print(f"\n[*] Post-Mitigation Results:")
            print(f"    - Validations Passed: {summary.get('passed', 0)}")
            print(f"    - Validations Failed: {summary.get('failed', 0)}")
        
        if self.results.get("comparison"):
            print(f"\n[*] Comparison:")
            print(f"    - Vulnerabilities Identified: {self.results['comparison']['pre_mitigation_vulnerabilities']}")
            print(f"    - Security Fixes Verified: {self.results['comparison']['post_mitigation_validations_passed']}")


def main():
    """Main entry point"""
    workspace_root = os.path.dirname(os.path.abspath(__file__))
    
    runner = MasterTestRunner(workspace_root)
    results = runner.run_all_tests()
    
    # Save results
    runner.save_results("comprehensive_test_results.json")
    
    # Print summary
    runner.print_summary()
    
    print("\n" + "="*80)
    print("[+] Complete test suite finished!")
    print(f"[+] Results file: comprehensive_test_results.json")
    print("="*80)


if __name__ == "__main__":
    main()
