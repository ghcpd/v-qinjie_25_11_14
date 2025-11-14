"""
Simulates a dashboard with insecure UI behaviors including leaked API keys,
exposed debug data, unsafe client-side execution, and verbose client logging.
"""

class VulnerableDashboard:
    API_KEY = "VULN-SECRET-KEY-12345"
    ADMIN_TOKEN = "admintoken_sensitive_data"

    def render_dashboard(self) -> str:
        """
        Returns HTML that shows the login form, API key, embedded secrets, and
        unsafe client scripts.
        """
        return f"""
        <html>
            <head>
                <title>Vulnerable Dashboard</title>
                <script>
                    // Secret embedded in frontend
                    const API_KEY = '{self.API_KEY}';
                    const ADMIN_TOKEN = '{self.ADMIN_TOKEN}';

                    function previewFile(payload) {{
                        // Unsafe use of eval on user-controlled payload
                        console.log('Preview request for payload:', payload);
                        const preview = eval(payload);
                        document.getElementById('file-preview').innerText = preview;
                    }}

                    function logSensitiveData() {{
                        console.log('Using API key:', API_KEY);
                        console.log('Using admin token:', ADMIN_TOKEN);
                    }}

                    function showDebugInfo() {{
                        const stackTrace = '{self.get_debug_info()}';
                        alert(stackTrace);  // Insecure UX flow leaking internal state
                    }}
                </script>
            </head>
            <body>
                <h1>Welcome back!</h1>
                <form id="login-form">
                    <label>Username <input type="text" name="user" /></label><br />
                    <label>Password <input type="password" name="pass" /></label><br />
                    <button type="button" onclick="logSensitiveData()">Log me in</button>
                </form>

                <section id="api-section">
                    <h2>API status</h2>
                    <div id="api-key-container">
                        <strong>Live API Key:</strong> <span>{self.API_KEY}</span>
                    </div>
                    <button onclick="showDebugInfo()">Show debug info (unsafe)</button>
                </section>

                <section id="file-preview-section">
                    <h3>File preview (unsafe)</h3>
                    <button onclick="previewFile('2 + 2')">Preview safe payload</button>
                    <button onclick="previewFile('alert(\\'owned by attacker\\')')">Preview attacker payload</button>
                    <pre id="file-preview">No preview yet.</pre>
                </section>
            </body>
        </html>
        """

    def get_debug_info(self) -> str:
        return "Traceback (most recent call last): insecure_module.py line 42"
