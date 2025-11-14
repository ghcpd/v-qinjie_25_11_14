from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "vuln-super-secret-session"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
API_KEY_VULN = "SENSITIVE_API_KEY_vuln_ABC123"

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

exfiltrations = []  # Store exfiltrated tokens (for test verification)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        session['user'] = user
        session['authenticated'] = True
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    # Vulnerable: API key is embedded in the page and in a public JS file
    return render_template('dashboard.html', api_key=API_KEY_VULN)

@app.route('/static/js/client.js')
def client_js():
    # This would normally be a static file served from disk; for convenience, return it from an endpoint
    # Vulnerable: the API key is embedded directly in JS and logged to console
    js = f"""
    // Vulnerable client-side script
    const API_KEY = '{API_KEY_VULN}';
    console.log('Client initialized. API_KEY:', API_KEY);

    function previewFile(fileContent) {{
        // Dangerous rendering: directly set innerHTML on the preview container
        const preview = document.getElementById('preview');
        preview.innerHTML = fileContent;
    }}

    function uploadPreview(file) {{
        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', {{method: 'POST', body: formData}})
            .then(response => response.json())
            .then(data => window.open('/preview/' + data.filename));
    }}
    """
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')
    f = request.files['file']
    filename = secure_filename(f.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    f.save(save_path)
    return jsonify({'filename': filename})

@app.route('/preview/<filename>')
def preview(filename):
    # Read the uploaded file and embed raw content directly into the page
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    # Vulnerable: we intentionally render the user-provided content unescaped, causing script execution
    return render_template('preview.html', content=content)

@app.route('/exfiltrate')
def exfiltrate():
    token = request.args.get('token')
    exfiltrations.append({'token': token})
    print('Exfiltrated token received:', token)
    return jsonify({'ok': True})

@app.route('/exfiltrations')
def get_exfiltrations():
    return jsonify(exfiltrations)

@app.route('/reset-exfiltrations', methods=['POST'])
def reset_exfiltrations():
    exfiltrations.clear()
    return jsonify({'ok': True})

@app.route('/debug-info')
def debug_info():
    # Vulnerable: show sensitive config and debug info in a UI endpoint
    return jsonify({
        'debug': app.debug,
        'secret': API_KEY_VULN,
        'session_key': app.secret_key
    })

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
