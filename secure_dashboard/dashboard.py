"""
Hardened dashboard implementation that avoids exposing secrets to the UI,
omits debug leaks, and sanitizes client-side execution.
"""

class SecureDashboard:
    API_KEY = "SECURE-KEY-67890"

    def render_dashboard(self) -> str:
        """
        Returns sanitized HTML: no API key display, no secrets in JS, and safe
        client-side execution path.
        """
        masked_key = self.API_KEY[:4] + "*" * 10
        return f"""
        <html>
            <head>
                <title>Secure Dashboard</title>
                <script>
                    function sanitizedPreview(payload) {{
                        const preview = payload.replace(/</g, "&lt;").replace(/>/g, "&gt;");
                        document.getElementById('file-preview').innerText = preview;
                    }}
                </script>
            </head>
            <body>
                <h1>Welcome back!</h1>
                <form id="login-form">
                    <label>Username <input type="text" name="user" /></label><br />
                    <label>Password <input type="password" name="pass" /></label><br />
                    <button type="submit">Log me in</button>
                </form>

                <section id="api-section">
                    <h2>API status</h2>
                    <div id="api-key-container">
                        <strong>Live API Key:</strong> <span>{masked_key}</span>
                        <p class="helper">Full key remains on the server. Request it via secure endpoint.</p>
                    </div>
                </section>

                <section id="file-preview-section">
                    <h3>File preview (safe)</h3>
                    <button onclick="sanitizedPreview('2 + 2')">Preview safe payload</button>
                    <button onclick="sanitizedPreview('<svg/onload=alert(1)>')">Preview attacker sample</button>
                    <pre id="file-preview">No preview yet.</pre>
                </section>
            </body>
        </html>
        """
