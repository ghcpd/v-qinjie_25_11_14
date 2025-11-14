// Hardened client helper that never embeds production secrets.
const API_STATUS_ELEMENT_ID = 'api-key';

document.addEventListener('DOMContentLoaded', () => {
  fetch('/api/token')
    .then((res) => res.json())
    .then((data) => {
      const el = document.getElementById(API_STATUS_ELEMENT_ID);
      if (el) {
        el.dataset.source = 'server-mask';
        el.innerText = data.masked_key;
      }
    })
    .catch(() => {
      const el = document.getElementById(API_STATUS_ELEMENT_ID);
      if (el) {
        el.innerText = 'masked';
      }
    });
});
