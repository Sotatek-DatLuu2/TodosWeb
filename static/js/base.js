console.log("base.js is loaded and running!");

// Helper function to get a cookie by name
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                console.log(`DEBUG: Found cookie '${name}':`, cookieValue);
                break;
            }
        }
    } else {
        console.log("DEBUG: No cookies found for getCookie(", name, ")");
    }
    return cookieValue;
}

// Logout function
function logout() {
    console.log("Logging out...");
    document.cookie = `access_token=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    document.cookie = `user_role=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    window.location.href = '/auth/login-page';
}


// Add Todo JS
const todoForm = document.getElementById('todoForm');
if (todoForm) {
    todoForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: false
        };

        try {
            const token = getCookie('access_token');
            if (!token) {
                throw new Error('Authentication token not found');
            }

            const response = await fetch('/todos/todo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                form.reset();
                alert('Todo created successfully!');
                window.location.href = '/todos/todo-page';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Edit Todo JS
const editTodoForm = document.getElementById('editTodoForm');
if (editTodoForm) {
    editTodoForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        var url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf('/') + 1);

        const payload = {
            title: data.title,
            description: data.description,
            priority: parseInt(data.priority),
            complete: data.complete === "on"
        };

        try {
            const token = getCookie('access_token');
            console.log("Edit Todo JS - Token from cookie:", token);
            if (!token) {
                throw new Error('Authentication token not found');
            }

            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Todo updated successfully!');
                window.location.href = '/todos/todo-page';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });

    document.getElementById('deleteButton').addEventListener('click', async function () {
        if (!confirm('Are you sure you want to delete this todo?')) {
            return;
        }

        var url = window.location.pathname;
        const todoId = url.substring(url.lastIndexOf('/') + 1);

        try {
            const token = getCookie('access_token');
            console.log("Delete Todo JS - Token from cookie:", token);
            if (!token) {
                throw new Error('Authentication token not found');
            }

            const response = await fetch(`/todos/todo/${todoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (response.ok) {
                alert('Todo deleted successfully!');
                window.location.href = '/todos/todo-page';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Login JS
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);

        const payload = new URLSearchParams();
        for (const [key, value] of formData.entries()) {
            payload.append(key, value);
        }

        try {
            const response = await fetch('/auth/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: payload.toString()
            });

            if (response.ok) {
                const data = await response.json();

                // LƯU TOKEN VÀ VAI TRÒ VÀO COOKIE
                document.cookie = `access_token=${data.access_token}; path=/; max-age=${60 * 30}`;
                document.cookie = `user_role=${data.user_role}; path=/; max-age=${60 * 30}`;

                console.log("Login successful! Redirecting...");
                console.log("Access Token from login response:", data.access_token);
                console.log("User Role from login response:", data.user_role);
                console.log("Current cookies after setting:", document.cookie);

                // Chuyển hướng dựa trên vai trò
                if (data.user_role === 'admin') {
                    window.location.href = '/admin/all-todos-page';
                } else {
                    window.location.href = '/todos/todo-page';
                }
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Register JS
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.password !== data.password2) {
            alert("Passwords do not match");
            return;
        }

        const payload = {
            email: data.email,
            username: data.username,
            first_name: data.first_name,
            last_name: data.last_name,
            role: data.role,
            phone_number: data.phone_number,
            password: data.password
        };

        try {
            const response = await fetch('/auth/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('User registered successfully! Please login.');
                window.location.href = '/auth/login-page';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Forgot Password JS
const forgotPasswordForm = document.getElementById('forgotPasswordForm');
if (forgotPasswordForm) {
    forgotPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(forgotPasswordForm);
        const email = formData.get('email');

        try {
            const response = await fetch('/auth/forgot-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email: email })
            });

            if (response.ok) {
                alert('If an account with that email exists, a password reset link has been sent to your email.');
                forgotPasswordForm.reset();
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail || 'Something went wrong.'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Reset Password JS
const resetPasswordForm = document.getElementById('resetPasswordForm');
if (resetPasswordForm) {
    resetPasswordForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(resetPasswordForm);
        const token = formData.get('token');
        const newPassword = formData.get('new_password');
        const confirmPassword = formData.get('confirm_password');

        if (newPassword !== confirmPassword) {
            alert('New password and confirm password do not match.');
            return;
        }

        try {
            const response = await fetch('/auth/reset-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: token, new_password: newPassword })
            });

            if (response.ok) {
                alert('Your password has been reset successfully. Please login with your new password.');
                resetPasswordForm.reset();
                window.location.href = '/auth/login-page';
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail || 'Something went wrong.'}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}

// Change Password JS (Đã đưa lại vào base.js)
const changePasswordForm = document.getElementById('changePasswordForm');
if (changePasswordForm) {
    changePasswordForm.addEventListener('submit', async function (event) {
        event.preventDefault();

        const form = event.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());

        if (data.new_password !== data.confirm_new_password) {
            alert("New password and confirm new password do not match");
            return;
        }

        const payload = {
            current_password: data.current_password,
            new_password: data.new_password
        };

        try {
            const token = getCookie('access_token');
            console.log("Change Password JS - Token from cookie:", token);
            if (!token) {
                throw new Error('Authentication token not found');
            }

            const response = await fetch('/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                alert('Password changed successfully! Please login again with your new password.');
                logout(); // Đăng xuất sau khi đổi mật khẩu để người dùng đăng nhập lại với mật khẩu mới
            } else {
                const errorData = await response.json();
                alert(`Error: ${errorData.detail}`);
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        }
    });
}
