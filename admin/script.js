
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const adminConsole = document.getElementById('admin-console');
    const loginContainer = document.getElementById('login-container');
    const ipDisplay = document.getElementById('ip-display');

    // Get admin's IP address
    fetch('https://ipinfo.io/json')
        .then(response => response.json())
        .then(data => {
            ipDisplay.textContent = `Your IP: ${data.ip}`;
        });

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === 'kaka' && password === 'sessionauthsupabase168233administrador') {
            loginContainer.style.display = 'none';
            adminConsole.style.display = 'block';
            loadUserData();
        } else {
            alert('Invalid credentials');
        }
    });

    function loadUserData() {
        const request = indexedDB.open('userDB', 1);

        request.onsuccess = (event) => {
            const db = event.target.result;
            const transaction = db.transaction(['users'], 'readonly');
            const objectStore = transaction.objectStore('users');
            const getAllRequest = objectStore.getAll();

            getAllRequest.onsuccess = () => {
                const userData = getAllRequest.result;
                const tableBody = document.getElementById('user-data-body');
                tableBody.innerHTML = '';
                userData.forEach(user => {
                    const row = tableBody.insertRow();
                    row.innerHTML = `
                        <td>${new Date(user.timestamp).toLocaleString()}</td>
                        <td>${user.ip}</td>
                        <td>${user.country}</td>
                        <td>${user.city}</td>
                        <td>${user.org}</td>
                    `;
                });
            };
        };
    }
});
