// This script needs to be executed in the browser console

// Wait for the login form to be ready
document.addEventListener('DOMContentLoaded', function () {
    console.log('Login form loaded');

    // Fill in username and password
    const usernameInput = document.querySelector('input[type="text"]');
    const passwordInput = document.querySelector('input[type="password"]');
    const loginButton = document.querySelector('button[type="submit"]');

    if (usernameInput && passwordInput && loginButton) {
        console.log('Form elements found');

        // Set values
        usernameInput.value = '12345678901';
        passwordInput.value = 'admin123';

        // Click login button
        loginButton.click();
        console.log('Login button clicked');
    } else {
        console.error('Form elements not found');
    }
});
