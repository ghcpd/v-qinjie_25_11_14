// Intentionally vulnerable file that exposes secrets and runs eval on preview payloads.
const HARDCODED_ADMIN_TOKEN = 'admin-secret-token-pre';
console.log('Shipping admin token to console for debugging', HARDCODED_ADMIN_TOKEN);

document.addEventListener('DOMContentLoaded', () => {
  window.replayPreviewPayload = function(payload) {
    // Dangerous: eval allows attackers to execute arbitrary JS from preview content.
    eval(payload);
  };
});
