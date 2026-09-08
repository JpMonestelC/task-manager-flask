// Shared by login.html and register.html.
//
// Toggles the password input between hidden and visible text. There is no
// "eye-slash" icon asset in this project yet, so the eye icon itself does
// not change when toggled - only the input's type does. Add a second icon
// and swap it here if that asset is ever added.
function togglePassword() {
    const passwordInput = document.getElementById('password');
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
    } else {
        passwordInput.type = 'password';
    }
}
