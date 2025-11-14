# SETUP GUIDE - UI Security Vulnerability Testing Suite

## Prerequisites

### System Requirements
- **OS**: Windows 10+, macOS, or Linux
- **Python**: 3.11 or higher
- **RAM**: 2GB minimum
- **Disk**: 500MB for installation and test data

### Software Installation

#### Windows

1. **Install Python 3.11+**
   - Download from https://www.python.org/
   - ✓ Check "Add Python to PATH" during installation
   - Verify: `python --version`

2. **Install Git (Optional)**
   - Download from https://git-scm.com/

3. **Text Editor/IDE (Recommended)**
   - VS Code: https://code.visualstudio.com/
   - PyCharm: https://www.jetbrains.com/pycharm/

#### macOS

```bash
# Install Python 3.11 using Homebrew
brew install python@3.11

# Create alias
alias python=/usr/local/opt/python@3.11/bin/python
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install python3.11 python3-pip python3-venv
```

## Installation Steps

### 1. Clone/Extract Project

```bash
# Option A: Clone from repository
git clone <repository-url>
cd v-qinjie_25_11_14

# Option B: Extract from ZIP
unzip ui-security-testing.zip
cd v-qinjie_25_11_14
```

### 2. Create Virtual Environment (Recommended)

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Install all required packages
pip install -r pre-mitigation/requirements.txt
pip install -r post-mitigation/requirements.txt

# Additional optional packages
pip install flask-debugtoolbar  # For development only
pip install pytest              # For advanced testing
```

### 4. Verify Installation

```bash
python -c "import flask; print(f'Flask {flask.__version__} installed')"
python -c "import requests; print(f'Requests {requests.__version__} installed')"
```

## Running the Test Suite

### Option 1: Complete Automated Test (RECOMMENDED)

**Windows:**
```cmd
run_all_tests.bat
```

**macOS/Linux:**
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

**Python (All platforms):**
```bash
python master_test_runner.py
```

### Option 2: Run Individual Tests

**Test Vulnerable Version:**
```bash
cd pre-mitigation
python tests/exploit_tests.py
```

Output: `exploit_results.json`

**Test Secure Version:**
```bash
cd post-mitigation
python tests/validation_tests.py
```

Output: `validation_results.json`

### Option 3: Manual Testing

**Start Vulnerable App:**
```bash
cd pre-mitigation/app
python app.py
```
- Access: http://localhost:5000
- Credentials: admin / password123

**Start Secure App:**
```bash
cd post-mitigation/app
export FLASK_DEBUG=False  # Unix
set FLASK_DEBUG=False     # Windows
python app.py
```
- Access: http://localhost:5001
- Credentials: admin / password123

## Test Output Files

### JSON Reports Generated

1. **exploit_results.json**
   - Location: `pre-mitigation/` or `results/`
   - Contains: All extracted vulnerabilities and secrets
   - Size: ~5-20 KB

2. **validation_results.json**
   - Location: `post-mitigation/` or `results/`
   - Contains: All security validation results
   - Size: ~3-10 KB

3. **pre_mitigation_report.json**
   - Comprehensive vulnerability details
   - Exploit steps, proof of concepts
   - Impact analysis

4. **post_mitigation_report.json**
   - Security fix summary
   - Implementation details
   - Verification results

### Markdown Reports Generated

- **REPORT_TEMPLATE.md** - Detailed security assessment report

## Interpreting Results

### Vulnerability Report Example

```json
{
  "exploits": [
    {
      "name": "API Key Leakage via Login Response",
      "success": true,
      "extracted_data": {
        "api_key": "sk_live_1234567890abcdef_secret_prod_key"
      },
      "evidence": "Credentials returned in plaintext JSON response"
    }
  ]
}
```

**Interpretation**: ✗ VULNERABLE - API keys exposed in plaintext

### Validation Report Example

```json
{
  "validations": [
    {
      "name": "No Secrets in Login Response",
      "passed": true,
      "details": ["✓ No API keys in response"]
    }
  ]
}
```

**Interpretation**: ✓ SECURE - Vulnerabilities fixed

## Troubleshooting

### Issue: "Python not found"
```
Solution:
1. Verify Python installation: python --version
2. Add Python to PATH
3. Restart terminal/command prompt
```

### Issue: "Module not found" (flask, requests, etc.)
```
Solution:
1. Activate virtual environment
2. Reinstall dependencies: pip install -r requirements.txt
3. Verify: pip list
```

### Issue: "Port already in use"
```
Solution:
1. Kill existing Python processes
   Windows: taskkill /F /IM python.exe
   Unix: pkill -f "python app.py"
2. Change port in app.py (modify port=5000/5001)
3. Wait a few seconds for port release
```

### Issue: "ConnectionRefusedError" during tests
```
Solution:
1. Verify app is running: netstat -tuln | grep 5000
2. Check app logs in results/ directory
3. Increase wait time in test scripts (change sleep 3 to sleep 5)
4. Verify no firewall blocking the connection
```

### Issue: Permission Denied on Linux/macOS
```
Solution:
1. Make scripts executable: chmod +x run_tests.sh
2. Run with python: python master_test_runner.py
```

## Advanced Usage

### Docker Installation

**Install Docker:**
- Windows: https://www.docker.com/products/docker-desktop
- macOS: https://www.docker.com/products/docker-desktop
- Linux: `sudo apt install docker.io`

**Build and Run:**
```bash
# Build vulnerable version
cd pre-mitigation
docker build -t vulnerable-dashboard .
docker run -p 5000:5000 vulnerable-dashboard

# Build secure version
cd ../post-mitigation
docker build -t secure-dashboard .
docker run -p 5001:5001 secure-dashboard
```

### Custom Configuration

**Pre-mitigation** (no env configuration needed - demonstrates vulnerabilities)

**Post-mitigation** (.env file in `post-mitigation/app/`):
```env
FLASK_DEBUG=False
ENVIRONMENT=production
SECRET_KEY=your-custom-secret-key
API_KEY=your-api-key
# ... other settings
```

## Performance Considerations

- **Vulnerable Version**: Intentionally slow due to debug features
  - Debug: True, exposing sensitive information
  - No optimization

- **Secure Version**: Optimized for production
  - Debug: False
  - Input validation overhead: ~1-5ms per request

## Next Steps

1. ✓ Review generated JSON reports
2. ✓ Read security findings in `pre_mitigation_report.json`
3. ✓ Examine security fixes in `post_mitigation_report.json`
4. ✓ Study patch implementation in code files
5. ✓ Review REPORT_TEMPLATE.md for comprehensive analysis

## Security Notes

⚠️ **IMPORTANT**: This is a demonstration project for educational purposes only
- DO NOT use the vulnerable version for any real application
- DO NOT expose credentials found in the reports
- DO NOT deploy vulnerable code to production
- The vulnerable version intentionally exposes secrets for demonstration

## Support Resources

- **Flask Documentation**: https://flask.palletsprojects.com/
- **OWASP Security**: https://owasp.org/
- **CWE Reference**: https://cwe.mitre.org/
- **Python Security**: https://python.readthedocs.io/en/latest/library/security_warnings.html

## Cleanup

To clean up test artifacts:

**Windows:**
```cmd
rmdir /s /q results
del *.json
del *.log
```

**macOS/Linux:**
```bash
rm -rf results
rm *.json
rm *.log
```

## Version Information

- **Python**: 3.11+
- **Flask**: 3.0.0
- **Requests**: 2.31.0
- **Flask-Talisman**: 1.1.0
- **Project Version**: 1.0
- **Date**: November 2024

## Feedback & Issues

For issues or questions:
1. Check troubleshooting section above
2. Review README.md for detailed information
3. Check generated logs in `results/` directory
4. Review test output for specific error messages
