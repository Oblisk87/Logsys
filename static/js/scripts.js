
// JavaScript code for frontend functionalities

async function login() {
    console.log("Login function called");
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
    });

    if (response.ok) {
        const data = await response.json();
        if (data.message === 'Login successful') {
            window.location.href = '/dashboard';
        } else {
            alert('Login failed: ' + data.detail);
        }
    } else {
        alert('Login failed: ' + response.statusText);
    }
}

function logout() {
    window.location.href = '/';
}

function showUserProfile(user) {
    const userProfile = document.createElement('div');
    userProfile.innerHTML = `
        <h2>User Profile</h2>
        <p>ID: ${user.id}</p>
        <p>Email: <input type="text" id="user-email" value="${user.email}"></p>
        <p>Username: <input type="text" id="user-username" value="${user.username}"></p>
        <p>Password: <input type="password" id="user-password" value=""></p>
        <p>Status: <input type="checkbox" id="user-status" ${user.status === 'active' ? 'checked' : ''}> Active</p>
        <button onclick="updateUser(${user.id})">Update</button>
        <button onclick="closeUserProfile()">Close</button>
    `;
    userProfile.style.position = 'fixed';
    userProfile.style.top = '50%';
    userProfile.style.left = '50%';
    userProfile.style.transform = 'translate(-50%, -50%)';
    userProfile.style.backgroundColor = 'white';
    userProfile.style.padding = '20px';
    userProfile.style.boxShadow = '0 0 10px rgba(0, 0, 0, 0.1)';
    document.body.appendChild(userProfile);
}

function closeUserProfile() {
    const userProfile = document.querySelector('div[style*="position: fixed"]');
    if (userProfile) {
        document.body.removeChild(userProfile);
    }
}

async function updateUser(userId) {
    const email = document.getElementById('user-email').value;
    const username = document.getElementById('user-username').value;
    const password = document.getElementById('user-password').value;
    const status = document.getElementById('user-status').checked ? 'active' : 'blocked';

    const response = await fetch('/users/' + userId, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, username, password, status })
    });

    if (response.ok) {
        alert('User updated successfully');
        closeUserProfile();
        fetchUsers();
    } else {
        alert('Failed to update user');
    }
}

async function fetchUsers() {
    console.log("Fetching users...");
    const response = await fetch('/users');
    const users = await response.json();
    console.log("Users fetched:", users);
    const userList = document.getElementById('user-list');
    userList.innerHTML = '';
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.textContent = `Username: ${user.username}, Email: ${user.email}, Status: ${user.status}`;
        userItem.onclick = function() {
            showUserProfile(user);
        };
        userList.appendChild(userItem);
    });
}

async function searchUser() {
    const query = document.getElementById('search-user').value;
    const response = await fetch(`/users?query=${query}`);
    const users = await response.json();
    const userList = document.getElementById('user-list');
    userList.innerHTML = '';
    users.forEach(user => {
        const userItem = document.createElement('div');
        userItem.textContent = `Username: ${user.username}, Email: ${user.email}, Status: ${user.status}`;
        userList.appendChild(userItem);
    });
}

async function fetchLogs() {
    console.log("Fetching logs...");
    const response = await fetch('/logs');
    const logs = await response.json();
    console.log("Logs fetched:", logs);
    const logList = document.getElementById('log-list');
    logList.innerHTML = '';
    logs.forEach(log => {
        const logItem = document.createElement('div');
        logItem.textContent = `Date: ${log.date}, Resource: ${log.resource_name}, Category: ${log.category}, Message: ${log.message}, Level: ${log.level}`;
        logList.appendChild(logItem);
    });
}

async function searchLog() {
    const query = document.getElementById('search-log').value;
    const response = await fetch(`/logs?query=${query}`);
    const logs = await response.json();
    const logList = document.getElementById('log-list');
    logList.innerHTML = '';
    logs.forEach(log => {
        const logItem = document.createElement('div');
        logItem.textContent = `Date: ${log.date}, Resource: ${log.resource_name}, Category: ${log.category}, Message: ${log.message}, Level: ${log.level}`;
        logList.appendChild(logItem);
    });
}

// Fetch users and logs on page load
window.onload = function() {
    console.log("Page loaded");
    fetchUsers();
    fetchLogs();
}
