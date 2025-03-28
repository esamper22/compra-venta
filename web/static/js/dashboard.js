// Sidebar Toggle
document.addEventListener('DOMContentLoaded', function() {
const sidebar = document.getElementById('sidebar');
const mainContent = document.getElementById('mainContent');
const sidebarToggle = document.getElementById('sidebarToggle');
const mobileMenuToggle = document.getElementById('mobileMenuToggle');
const themeToggle = document.getElementById('themeToggle');

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme') || 'light';
document.documentElement.setAttribute('data-bs-theme', savedTheme);
updateThemeIcon();

// Toggle sidebar on desktop
sidebarToggle.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
});

// Toggle sidebar on mobile
mobileMenuToggle.addEventListener('click', function() {
    sidebar.classList.toggle('show');
});

// Close sidebar when clicking outside on mobile
document.addEventListener('click', function(event) {
    const isClickInsideSidebar = sidebar.contains(event.target);
    const isClickOnMobileToggle = mobileMenuToggle.contains(event.target);
    
    if (!isClickInsideSidebar && !isClickOnMobileToggle && window.innerWidth < 992) {
    sidebar.classList.remove('show');
    }
});

// Theme toggle
themeToggle.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    updateThemeIcon();
});

function updateThemeIcon() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    themeToggle.innerHTML = currentTheme === 'dark' 
    ? '<i class="fas fa-sun"></i>' 
    : '<i class="fas fa-moon"></i>';
}

// Handle tab navigation
const tabLinks = document.querySelectorAll('.nav-link[data-bs-toggle="tab"]');
tabLinks.forEach(link => {
    link.addEventListener('click', function() {
    // Remove active class from all links
    tabLinks.forEach(l => l.classList.remove('active'));
    // Add active class to clicked link
    this.classList.add('active');
    
    // Close sidebar on mobile when a link is clicked
    if (window.innerWidth < 992) {
        sidebar.classList.remove('show');
    }
    });
});
});
