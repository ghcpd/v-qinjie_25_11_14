from flask import Flask, render_template, request, jsonify, redirect, url_for
import threading
import logging
import os
import uuid
import bleach

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsecret'
# Backend-only API key (never exposed to client)
app.config['API_KEY'] = 'POST_PATCH_API_KEY_XYZ987654'

# In-memory store of ephemeral tokens (unsafe long-term in real apps)
EPHEMERAL_TOKENS = {}

# Basic in-memory users
USERS = {'alice': 'password123'}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if USERS.get(username) == password:
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Show only masked API key (last 4 chars) to avoid full exposure
    full = app.config['API_KEY']
    masked = '****' + full[-4:]
    return render_template('dashboard.html', api_key=masked)

@app.route('/api/token', methods=['POST'])
def api_token():
    # Generate ephemeral token - server-side only
    token = str(uuid.uuid4())
    EPHEMERAL_TOKENS[token] = {'allowed': True}
    return jsonify({'token': token})

@app.route('/api/use')
def api_use():
    # Require ephemeral token in header
    token = request.headers.get('X-Ephemeral-Token')
    if token and EPHEMERAL_TOKENS.get(token):
        # Do not log secrets
        return jsonify({'result': 'used'})
    return jsonify({'error': 'invalid token'}), 403

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        f = request.files.get('file')
        content = f.read().decode('utf-8')
        # Mitigation: sanitize and remove script tags and dangerous HTML
        safe = bleach.clean(content, tags=['b','i','u','em','strong','p','br','ul','li','ol','span'], strip=True)
        return render_template('preview.html', content=safe)
    return render_template('upload.html')

@app.route('/debug')
def debug():
    # Mitigation: only allow admin access via header
    if request.headers.get('X-ADMIN') == 'true':
        return jsonify({'debug': True, 'msg': 'admin only'})
    return jsonify({'debug': False}), 403

@app.route('/static/js/app.js')
def app_js():
    # No embedded secrets, only small helper functions; ephemeral tokens are fetched via endpoint
    js = """
console.log('App JS loaded');

function fetchToken() {
    return fetch('/api/token', {method: 'POST'})
        .then(r => r.json())
        .then(j => j.token)
}

async function callApi() {
    const token = await fetchToken();
    return fetch('/api/use', {headers: {'X-Ephemeral-Token': token}}).then(r => r.json()).then(console.log)
}
"""
    return app.response_class(js, mimetype='application/javascript')

# Run the server if executed directly
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=False)
