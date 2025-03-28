
// Animate elements when they come into view
document.addEventListener('DOMContentLoaded', function() {
const animateElements = document.querySelectorAll('.animate__animated');

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
    if (entry.isIntersecting) {
        entry.target.style.visibility = 'visible';
        entry.target.classList.add('animate__fadeInUp');
        observer.unobserve(entry.target);
    }
    });
}, {
    threshold: 0.1
});

animateElements.forEach(element => {
    if (!element.classList.contains('animate__fadeInDown') && 
        !element.classList.contains('animate__fadeInUp')) {
    element.style.visibility = 'hidden';
    observer.observe(element);
    }
});
});