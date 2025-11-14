"""
VULNERABLE WEB DASHBOARD - Pre-Mitigation Version
This application intentionally contains multiple UI security vulnerabilities:
1. API keys exposed in responses
2. Secrets embedded in frontend JavaScript
3. Unsafe file preview with XSS vulnerability
4. Client-side logging leaking sensitive data
5. Debug info and stack traces exposed
"""

from flask import Flask, render_template, request, jsonify, session
import os
import json
import traceback
from functools import wraps

app = Flask(__name__)
app.secret_key = "insecure_secret_key_123456"

# VULNERABILITY 1: Hardcoded secrets and API keys
API_KEY = "sk_live_1234567890abcdef_secret_prod_key"
DATABASE_PASSWORD = "admin_password_db_2024"
STRIPE_KEY = "sk_test_stripe_key_12345"
INTERNAL_API_URL = "http://internal.company.local/api/v1"
SERVICE_ACCOUNT_KEY = "service_account_key_xyz789"

# VULNERABILITY 2: Global state that logs sensitive data
debug_logs = []

def log_debug_message(msg, context=None):
    """VULNERABLE: Logs sensitive data without filtering"""
    debug_logs.append({
        "message": msg,
        "context": context,
        "timestamp": str(__import__('datetime').datetime.now())
    })

# VULNERABILITY 3: Insecure error handling exposing stack traces
def handle_errors(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # VULNERABILITY: Returns full stack trace and system info
            return jsonify({
                "error": str(e),
                "traceback": traceback.format_exc(),
                "debug_info": {
                    "python_version": __import__('sys').version,
                    "platform": __import__('platform').platform(),
                    "cwd": os.getcwd(),
                    "env_vars": dict(os.environ)
                }
            }), 500
    return decorated

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with insecure practices"""
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        # VULNERABILITY: Credentials in logs
        log_debug_message(f"Login attempt", {
            "username": username,
            "password": password,
            "ip": request.remote_addr
        })
        
        if username == "admin" and password == "password123":
            session['user'] = username
            session['api_key'] = API_KEY  # VULNERABILITY: API key in session
            session['db_pass'] = DATABASE_PASSWORD  # VULNERABILITY: DB password in session
            
            # VULNERABILITY: Returns sensitive data in response
            return jsonify({
                "success": True,
                "user": username,
                "api_key": API_KEY,  # EXPOSED!
                "stripe_key": STRIPE_KEY,  # EXPOSED!
                "internal_endpoint": INTERNAL_API_URL,  # EXPOSED!
                "service_account": SERVICE_ACCOUNT_KEY  # EXPOSED!
            })
        
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard with exposed secrets"""
    if 'user' not in session:
        return redirect('/login')
    
    # VULNERABILITY: Template exposes API keys directly
    return render_template('dashboard.html', 
        api_key=API_KEY,
        stripe_key=STRIPE_KEY,
        user=session.get('user'),
        internal_api=INTERNAL_API_URL
    )

@app.route('/api/user-data')
@handle_errors
def get_user_data():
    """API endpoint returning user data with exposed secrets"""
    if 'user' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    # VULNERABILITY: Returns all sensitive data
    return jsonify({
        "user": session.get('user'),
        "api_key": API_KEY,
        "database_password": DATABASE_PASSWORD,
        "stripe_key": STRIPE_KEY,
        "internal_api_url": INTERNAL_API_URL,
        "service_account_key": SERVICE_ACCOUNT_KEY,
        "session_data": dict(session),  # VULNERABILITY: Exposes entire session
        "environment_config": {
            "flask_debug": app.debug,
            "secret_key": app.secret_key,
            "config": dict(app.config)
        }
    })

@app.route('/api/preview-file', methods=['POST'])
@handle_errors
def preview_file():
    """File preview endpoint - VULNERABLE to XSS and path traversal"""
    file_content = request.form.get('content', '')
    filename = request.form.get('filename', 'unknown')
    
    # VULNERABILITY 4: Unsafe file preview with no sanitization
    # Directly renders user-provided content in HTML response
    return jsonify({
        "filename": filename,
        "preview": file_content,  # NO SANITIZATION!
        "html": f"""
        <html>
        <head><title>Preview: {filename}</title></head>
        <body>
            <h1>File Preview</h1>
            <div id="content">{file_content}</div>
            <script>
                // This script tag and content can be injected!
                document.getElementById('content').innerHTML = `{file_content}`;
            </script>
        </body>
        </html>
        """
    })

@app.route('/api/render-data', methods=['POST'])
def render_data():
    """Endpoint for client-side rendering - VULNERABLE to DOM XSS"""
    data = request.json
    user_input = data.get('data', '')
    
    # VULNERABILITY 5: Unsafe rendering of user input
    return jsonify({
        "rendered": user_input,  # No escaping or sanitization
        "client_code": f"""
        <script>
            // VULNERABLE: Direct HTML injection
            var userInput = '{user_input}';
            document.body.innerHTML += userInput;
            
            // VULNERABILITY: Client-side logging of sensitive data
            console.log('User Input:', userInput);
            console.log('Session Data:', {json.dumps(dict(session))});
            console.log('API Key:', '{API_KEY}');
            console.log('All Secrets:', {{
                api_key: '{API_KEY}',
                stripe_key: '{STRIPE_KEY}',
                db_password: '{DATABASE_PASSWORD}'
            }});
        </script>
        """
    })

@app.route('/api/debug-info')
def debug_info():
    """Debug endpoint exposing all internal information"""
    # VULNERABILITY 6: Complete debug info endpoint
    return jsonify({
        "debug_logs": debug_logs,
        "all_secrets": {
            "api_key": API_KEY,
            "stripe_key": STRIPE_KEY,
            "database_password": DATABASE_PASSWORD,
            "service_account_key": SERVICE_ACCOUNT_KEY,
            "internal_api_url": INTERNAL_API_URL
        },
        "app_config": {
            "debug": app.debug,
            "testing": app.testing,
            "secret_key": app.secret_key,
            "all_config": dict(app.config)
        },
        "session_info": dict(session),
        "environment": {
            "python_version": __import__('sys').version,
            "platform": __import__('platform').platform(),
            "working_dir": os.getcwd(),
            "env_vars": {k: v for k, v in os.environ.items() if not k.startswith('_')}
        }
    })

@app.route('/api/source-code')
def source_code():
    """VULNERABILITY: Source code disclosure"""
    try:
        with open(__file__, 'r') as f:
            return jsonify({
                "source_code": f.read(),
                "file_path": __file__
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # VULNERABILITY: Running in debug mode with debug toolbar
    app.run(debug=True, host='0.0.0.0', port=5000)
