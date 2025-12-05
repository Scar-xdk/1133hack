
document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    const adminConsole = document.getElementById('admin-console');
    const loginContainer = document.getElementById('login-container');
    const ipDisplay = document.getElementById('ip-display');
    const logoutButton = document.getElementById('logout-button');

    if (sessionStorage.getItem('isAdminLoggedIn') === 'true') {
        showAdminConsole();
    }

    fetch('https://ipinfo.io/json')
        .then(response => response.json())
        .then(data => {
            ipDisplay.textContent = `Seu IP: ${data.ip}`;
        });

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === 'kaka' && password === 'sessionauthsupabase168233administrador') {
            sessionStorage.setItem('isAdminLoggedIn', 'true');
            showAdminConsole();
        } else {
            alert('Credenciais invÃ¡lidas');
        }
    });

    logoutButton.addEventListener('click', () => {
        sessionStorage.removeItem('isAdminLoggedIn');
        loginContainer.style.display = 'block';
        adminConsole.style.display = 'none';
    });

    function showAdminConsole() {
        loginContainer.style.display = 'none';
        adminConsole.style.display = 'block';
        loadUserData();
    }

    function loadUserData() {
        const request = indexedDB.open('userDB', 1);

        request.onupgradeneeded = event => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('users')) {
                db.createObjectStore('users', { keyPath: 'timestamp' });
            }
        };

        request.onsuccess = (event) => {
            const db = event.target.result;
             if (!db.objectStoreNames.contains('users')) {
                const tableBody = document.getElementById('user-data-body');
                tableBody.innerHTML = '<tr><td colspan="5">Ainda nÃ£o hÃ¡ dados de visitantes.</td></tr>';
                return;
            }
            const transaction = db.transaction(['users'], 'readonly');
            const objectStore = transaction.objectStore('users');
            const getAllRequest = objectStore.getAll();

            getAllRequest.onsuccess = () => {
                const userData = getAllRequest.result.reverse();
                const tableBody = document.getElementById('user-data-body');
                tableBody.innerHTML = '';
                if (userData.length === 0) {
                     tableBody.innerHTML = '<tr><td colspan="5">Nenhum dado de visitante ainda. Os dados aparecerÃ£o aqui quando os usuÃ¡rios visitarem a pÃ¡gina do gerador.</td></tr>';
                } else {
                    userData.forEach(user => {
                        const row = tableBody.insertRow();
                        row.innerHTML = `
                            <td>${new Date(user.timestamp).toLocaleString('pt-BR')}</td>
                            <td>${user.ip}</td>
                            <td>${user.country}</td>
                            <td>${user.city}</td>
                            <td>${user.org}</td>
                        `;
                    });
                }
            };
             getAllRequest.onerror = (event) => {
                console.error("Erro ao buscar dados do IndexedDB:", event.target.errorCode);
                 const tableBody = document.getElementById('user-data-body');
                 tableBody.innerHTML = `<tr><td colspan="5">Erro ao carregar dados: ${event.target.errorCode}</td></tr>`;
            };
        };

        request.onerror = (event) => {
            console.error("Erro no IndexedDB:", event.target.errorCode);
             const tableBody = document.getElementById('user-data-body');
             tableBody.innerHTML = `<tr><td colspan="5">NÃ£o foi possÃ­vel acessar o banco de dados local (IndexedDB).</td></tr>`;
        };
    }
});
