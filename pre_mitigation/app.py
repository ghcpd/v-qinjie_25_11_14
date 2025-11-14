from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import threading
import logging
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'devsecret'
# Vulnerable: API key embedded directly in frontend
app.config['API_KEY'] = 'PRE_VULN_API_KEY_ABC123456'

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
            # Set a fake session token
            token = 'session-token-{}'.format(username)
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Vulnerable: render API key in DOM and in JS
    api_key = app.config['API_KEY']
    return render_template('dashboard.html', api_key=api_key)

@app.route('/api/use')
def api_use():
    # Simulate use of API key for backend operation
    api_key = request.headers.get('X-API-KEY')
    if api_key == app.config['API_KEY']:
        # Vulnerable: log the api key
        app.logger.info('Using API key: %s', api_key)
        return jsonify({'result': 'used', 'api_key': api_key})
    return jsonify({'error': 'invalid key'}), 403

@app.route('/preview', methods=['GET', 'POST'])
def preview():
    if request.method == 'POST':
        f = request.files.get('file')
        content = f.read().decode('utf-8')
        # Vulnerable: directly render file content without escaping
        return render_template('preview.html', content=content)
    return render_template('upload.html')

@app.route('/debug')
def debug():
    # Vulnerable: display internal config for debugging via query param
    if request.args.get('show') == '1':
        return jsonify({'secret_key': app.config['SECRET_KEY'], 'api_key': app.config['API_KEY'], 'debug': True})
    return jsonify({'debug': False})

# Static JS that contains the API key - vulnerable
@app.route('/static/js/app.js')
def app_js():
    # Embed the API key in JS source
    js = f"""
console.log('App JS loaded');
const apiKey = '{app.config['API_KEY']}';
// Vulnerable: store API key in localStorage and log it
localStorage.setItem('apiKey', apiKey);
console.log('EXPOSED API KEY:', apiKey);

function callApi() {
    return fetch('/api/use', {headers: {'X-API-KEY': apiKey}})
        .then(r => r.json())
        .then(console.log)
}
"""
    return app.response_class(js, mimetype='application/javascript')

# Run the server if executed directly
if __name__ == '__main__':
    # Setup logging to console
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=5000, debug=False)
