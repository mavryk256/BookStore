document.getElementById('loginForm').addEventListener('submit', function(event) {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const loginError = document.getElementById('loginError');

    if (!username || !password) {
        event.preventDefault();
        loginError.textContent = 'Vui lòng nhập đầy đủ thông tin!';
        return;
    }


    loginError.textContent = ''; 
});

