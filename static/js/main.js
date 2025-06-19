// Password visibility toggle functionality
function setupPasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const toggleConfirmPassword = document.getElementById('toggleConfirmPassword');
    const passwordInput = document.getElementById('passwordInput');
    const confirmPasswordInput = document.getElementById('confirmPasswordInput');

    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    if (toggleConfirmPassword && confirmPasswordInput) {
        toggleConfirmPassword.addEventListener('click', function() {
            const type = confirmPasswordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            confirmPasswordInput.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }
}

// Initialize password toggle when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    setupPasswordToggle();
});

function formatISTDateTime(utcDateString) {
    if (!utcDateString) return 'N/A';
    return new Date(utcDateString).toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    });
}

// Update any dynamic timestamp displays
function updateTimestampDisplays() {
    document.querySelectorAll('[data-timestamp]').forEach(element => {
        const utcTimestamp = element.dataset.timestamp;
        if (utcTimestamp) {
            element.textContent = formatISTDateTime(utcTimestamp);
        }
    });
}

// Call this when the page loads and after any dynamic content updates
document.addEventListener('DOMContentLoaded', updateTimestampDisplays); 