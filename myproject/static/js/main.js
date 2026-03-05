// Simple helper scripts for site

// auto-hide flash messages after a few seconds
window.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(a => {
        setTimeout(() => { a.style.display = 'none'; }, 5000);
    });
});
