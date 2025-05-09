document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const phone = document.getElementById('phone').value;

    const emailPattern = /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/;
    if (!emailPattern.test(email)) {
        alert('Email không hợp lệ!');
        return;
    }

    if (password.length < 8) {
        alert('Mật khẩu phải từ 8 ký tự trở lên!');
        return;
    }

    if (password !== confirmPassword) {
        alert('Mật khẩu không khớp!');
        return;
    }

    const phonePattern = /^[0-9]{10}$/;
    if (!phonePattern.test(phone)) {
        alert('Số điện thoại phải là 10 chữ số!');
        return;
    }

    this.submit();
});

function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const toggle = field.nextElementSibling;
    if (field.type === 'password') {
        field.type = 'text';
        toggle.textContent = '👀'; 
    } else {
        field.type = 'password';
        toggle.textContent = '👁'; 
    }
}