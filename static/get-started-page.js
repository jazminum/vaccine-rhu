document.addEventListener('DOMContentLoaded', () => {
    const getStartedBtn = document.getElementById('getStartedBtn');

        getStartedBtn.addEventListener('click', () => {
        // Redirect to login page
        // Use 'login.html' if working with local files
        // Use '/login' if working with a Flask/Python backend
        setTimeout(() => {
            window.location.href = "login-page.html";
        }, 300);
        });
    }
);