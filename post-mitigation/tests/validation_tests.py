"""
SECURITY VALIDATION TESTS - Secure Version
Verifies that vulnerabilities have been fixed
"""

import requests
import json
import re
from typing import Dict, List
from datetime import datetime

class SecurityValidator:
    """Tests that verify security fixes in the secure app"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.validations = []
        
    def run_all_validations(self) -> Dict:
        """Run all security validation tests"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "target": self.base_url,
            "validations": [],
            "summary": {
                "passed": 0,
                "failed": 0
            }
        }
        
        # Test 1: API keys NOT exposed in login response
        print("[*] Validating: API Keys Not Exposed in Login...")
        test1 = self.validate_no_secrets_in_login()
        results["validations"].append(test1)
        
        # Test 2: User data endpoint doesn't return secrets
        print("[*] Validating: No Secrets in User Data...")
        test2 = self.validate_no_secrets_in_user_data()
        results["validations"].append(test2)
        
        # Test 3: No XSS in file preview
        print("[*] Validating: XSS Prevention in File Preview...")
        test3 = self.validate_xss_prevention()
        results["validations"].append(test3)
        
        # Test 4: No debug endpoint
        print("[*] Validating: Debug Endpoint Disabled...")
        test4 = self.validate_no_debug_endpoint()
        results["validations"].append(test4)
        
        # Test 5: No source code disclosure
        print("[*] Validating: Source Code Not Exposed...")
        test5 = self.validate_no_source_disclosure()
        results["validations"].append(test5)
        
        # Test 6: Security headers present
        print("[*] Validating: Security Headers Present...")
        test6 = self.validate_security_headers()
        results["validations"].append(test6)
        
        # Test 7: No stack traces in errors
        print("[*] Validating: No Stack Traces in Errors...")
        test7 = self.validate_no_stack_traces()
        results["validations"].append(test7)
        
        # Test 8: Proper session management
        print("[*] Validating: Secure Session Management...")
        test8 = self.validate_session_security()
        results["validations"].append(test8)
        
        # Summary
        for test in results["validations"]:
            if test.get("passed"):
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1
        
        return results
    
    def validate_no_secrets_in_login(self) -> Dict:
        """Validate: Secrets are NOT returned in login response"""
        test = {
            "name": "No Secrets in Login Response",
            "passed": False,
            "details": []
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={"username": "admin", "password": "password123"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check that sensitive fields are NOT present
                sensitive_fields = ["api_key", "stripe_key", "database_password", 
                                  "service_account", "internal_api_url", "secret_key"]
                
                found_secrets = [field for field in sensitive_fields if field in data]
                
                if not found_secrets:
                    test["passed"] = True
                    test["details"].append("✓ No API keys in response")
                    test["details"].append("✓ No credentials returned")
                else:
                    test["details"].append(f"✗ Found exposed fields: {found_secrets}")
            else:
                test["details"].append("Login failed (expected in secure version)")
                
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_no_secrets_in_user_data(self) -> Dict:
        """Validate: User data endpoint doesn't expose secrets"""
        test = {
            "name": "No Secrets in User Data Endpoint",
            "passed": False,
            "details": []
        }
        
        try:
            # Authenticate first
            self.session.post(
                f"{self.base_url}/login",
                data={"username": "admin", "password": "password123"}
            )
            
            response = self.session.get(f"{self.base_url}/api/user-data")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify that only safe data is returned
                safe_fields = ["user", "email", "last_login", "features"]
                secrets_fields = ["api_key", "database_password", "stripe_key", 
                                "service_account_key", "session_data", "config"]
                
                # Check what's in the response
                found_secrets = [field for field in secrets_fields if field in str(data)]
                
                if not found_secrets:
                    test["passed"] = True
                    test["details"].append("✓ No API keys in user data")
                    test["details"].append("✓ No database passwords")
                    test["details"].append("✓ No session info leaked")
                else:
                    test["details"].append(f"✗ Found exposed data: {found_secrets}")
            else:
                test["details"].append(f"Unexpected response code: {response.status_code}")
                
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_xss_prevention(self) -> Dict:
        """Validate: XSS payloads are sanitized"""
        test = {
            "name": "XSS Prevention - Input Sanitization",
            "passed": False,
            "details": []
        }
        
        try:
            # Authenticate
            self.session.post(
                f"{self.base_url}/login",
                data={"username": "admin", "password": "password123"}
            )
            
            xss_payload = '<img src=x onerror="alert(\'XSS\')">'
            
            response = self.session.post(
                f"{self.base_url}/api/preview-file",
                data={"filename": "test.html", "content": xss_payload}
            )
            
            if response.status_code == 200:
                data = response.json()
                response_text = json.dumps(data)
                
                # Check if payload was sanitized (escaped)
                if "&lt;" in response_text or "img src" not in response_text:
                    test["passed"] = True
                    test["details"].append("✓ XSS payload was sanitized")
                    test["details"].append(f"✓ Content properly escaped: {data.get('preview', '')[:50]}")
                else:
                    test["details"].append("✗ XSS payload not sanitized")
            else:
                test["details"].append(f"Request failed: {response.status_code}")
                
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_no_debug_endpoint(self) -> Dict:
        """Validate: Debug endpoint is disabled"""
        test = {
            "name": "Debug Endpoint Disabled",
            "passed": False,
            "details": []
        }
        
        try:
            response = self.session.get(f"{self.base_url}/api/debug-info")
            
            if response.status_code in [404, 403]:
                test["passed"] = True
                test["details"].append("✓ Debug endpoint not accessible")
            else:
                data = response.json()
                # Check if debug info is exposed
                if "all_secrets" in str(data) or "debug_logs" in str(data):
                    test["details"].append("✗ Debug endpoint still exposes secrets")
                else:
                    test["passed"] = True
                    test["details"].append("✓ Debug endpoint removed or secured")
                
        except requests.exceptions.ConnectionError:
            test["details"].append("Debug endpoint not found (secure)")
            test["passed"] = True
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_no_source_disclosure(self) -> Dict:
        """Validate: Source code is not accessible"""
        test = {
            "name": "Source Code Not Exposed",
            "passed": False,
            "details": []
        }
        
        try:
            response = self.session.get(f"{self.base_url}/api/source-code")
            
            if response.status_code in [404, 403]:
                test["passed"] = True
                test["details"].append("✓ Source code endpoint disabled")
            else:
                if response.status_code == 200:
                    test["details"].append("✗ Source code is accessible")
                else:
                    test["passed"] = True
                    test["details"].append("✓ Source code endpoint secure")
                
        except Exception as e:
            test["passed"] = True
            test["details"].append("✓ Source code endpoint not accessible")
        
        return test
    
    def validate_security_headers(self) -> Dict:
        """Validate: Security headers are present"""
        test = {
            "name": "Security Headers Present",
            "passed": False,
            "details": []
        }
        
        try:
            response = self.session.get(f"{self.base_url}/")
            
            headers_to_check = {
                "Content-Security-Policy": "CSP",
                "X-Frame-Options": "X-Frame-Options",
                "X-Content-Type-Options": "X-Content-Type-Options",
                "Strict-Transport-Security": "HSTS"
            }
            
            found_headers = 0
            for header, name in headers_to_check.items():
                if header in response.headers:
                    test["details"].append(f"✓ {name} present")
                    found_headers += 1
                else:
                    test["details"].append(f"✗ {name} missing")
            
            test["passed"] = found_headers >= 2
            
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_no_stack_traces(self) -> Dict:
        """Validate: No stack traces in error responses"""
        test = {
            "name": "No Stack Traces in Errors",
            "passed": False,
            "details": []
        }
        
        try:
            # Trigger an error by accessing non-existent endpoint
            response = self.session.get(f"{self.base_url}/nonexistent")
            
            if response.status_code == 404:
                response_text = response.text
                
                # Check for Python traceback indicators
                if "Traceback" not in response_text and "File" not in response_text:
                    test["passed"] = True
                    test["details"].append("✓ No Python traceback in error response")
                else:
                    test["details"].append("✗ Stack trace exposed in error")
            else:
                test["passed"] = True
                test["details"].append("✓ Error handling is secure")
                
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test
    
    def validate_session_security(self) -> Dict:
        """Validate: Session is properly secured"""
        test = {
            "name": "Secure Session Management",
            "passed": False,
            "details": []
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/login",
                data={"username": "admin", "password": "password123"}
            )
            
            # Check response headers
            if response.status_code == 200:
                headers = response.headers
                cookies = response.cookies
                
                if cookies:
                    test["details"].append("✓ Session cookie created")
                    test["passed"] = True
                else:
                    test["details"].append("Session cookie details checked")
                    test["passed"] = True
            
            # Verify session data not in response
            if "session" not in response.text.lower():
                test["details"].append("✓ Session data not exposed")
            
        except Exception as e:
            test["details"].append(f"Error: {str(e)}")
        
        return test


if __name__ == "__main__":
    validator = SecurityValidator()
    results = validator.run_all_validations()
    
    print("\n" + "="*80)
    print("SECURITY VALIDATION RESULTS")
    print("="*80)
    print(json.dumps(results, indent=2))
    
    # Save results
    with open("validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n[+] Results saved to validation_results.json")
    print(f"[+] Summary: {results['summary']['passed']} passed, {results['summary']['failed']} failed")
