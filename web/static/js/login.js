function togglePassword() {
const passwordInput = document.getElementById('password');
const toggleIcon = document.getElementById('toggleIcon');

if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    toggleIcon.classList.remove('fa-eye');
    toggleIcon.classList.add('fa-eye-slash');
} else {
    passwordInput.type = 'password';
    toggleIcon.classList.remove('fa-eye-slash');
    toggleIcon.classList.add('fa-eye');
}
}

// Add floating animation to decorative elements
document.addEventListener('DOMContentLoaded', function() {
const decorations = document.querySelectorAll('.login-decoration');

decorations.forEach(element => {
    // Random animation duration between 6-10s
    const duration = Math.floor(Math.random() * 5) + 6;
    element.style.animation = `float ${duration}s ease-in-out infinite`;
});
});
