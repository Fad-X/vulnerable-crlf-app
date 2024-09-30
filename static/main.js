document.querySelector('.login-form').addEventListener('submit', function() {
    const button = this.querySelector('button');
    button.innerText = 'Logging in...'; // Change button text
    button.disabled = true; // Disable button to prevent multiple submits
});

document.querySelector('.register-form').addEventListener('submit', function() {
    const button = this.querySelector('button');
    button.innerText = 'Registering...'; // Change button text
    button.disabled = true; // Disable button to prevent multiple submits
});
