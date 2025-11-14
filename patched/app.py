from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
import bleach

app = Flask(__name__)
app.secret_key = "patched-super-secret-session"
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
API_KEY_PATCHED = "SENSITIVE_API_KEY_patched_DEF456"

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

exfiltrations = []

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
    # Mask the API key in the UI. No full key in JS or HTML.
    masked = API_KEY_PATCHED[0] + '*' * (len(API_KEY_PATCHED) - 4) + API_KEY_PATCHED[-3:]
    return render_template('dashboard.html', api_key_masked=masked)

@app.route('/api/get_api_key')
def get_api_key():
    if not session.get('authenticated'):
        return jsonify({'error': 'unauthorized'}), 403
    # Do NOT return the full API key, send masked form or require additional auth to retrieve full key
    return jsonify({'api_key_masked': API_KEY_PATCHED[0] + '*' * (len(API_KEY_PATCHED) - 4) + API_KEY_PATCHED[-3:]})

@app.route('/static/js/client.js')
def client_js():
    # Patched client: no secrets, no console logs that reveal the API key
    js = """
    // Patched client-side script: no embedded API keys. Use fetch to request masked key.
    function requestMaskedKey() {
        fetch('/api/get_api_key').then(r => r.json()).then(j => {
            const elem = document.getElementById('api-key');
            if(elem) elem.textContent = 'API Key: ' + j.api_key_masked;
        });
    }

    function previewFile(fileContent) {
        const preview = document.getElementById('preview');
        // Instead of innerHTML, use textContent and sanitize HTML input to avoid script execution
        preview.textContent = fileContent;
    }

    function uploadPreview(file) {
        const formData = new FormData();
        formData.append('file', file);
        fetch('/upload', {method: 'POST', body: formData})
            .then(response => response.json())
            .then(data => window.open('/preview/' + data.filename));
    }
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
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return 'File not found', 404
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as fh:
        content = fh.read()
    # Sanitization before rendering: remove script tags and event attributes
    content_safe = bleach.clean(content, tags=['b', 'i', 'u', 'strong', 'em', 'p', 'br', 'pre'], attributes={}, strip=True)
    # Render as text content only to avoid script execution
    return render_template('preview.html', content=content_safe)

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
    # Patched: do not provide debug info or secrets via UI
    return 'Access denied', 403

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    # NOTE: debug must be False in production to avoid debug info leak
    app.run(debug=False, host='127.0.0.1', port=5001)
