// Sample user data
var allUsers = [
    { id: 1, userid: 'JDoe1', name: 'John Doe', email: 'johndoe@example.com', status: 'active' },
    { id: 2, userid: 'JSmith1', name: 'Jane Smith', email: 'janesmith@example.com', status: 'deactivated' },
    { id: 3, userid: 'MJohnson1', name: 'Mike Johnson', email: 'mikejohnson@example.com', status: 'active' },
];

var searchTerm = '';
var selectedStatus = '';

// Function to render the user list with filters applied
function renderUserList() {
    var userTableBody = document.getElementById('user-table-body');
    userTableBody.innerHTML = '';

    var filteredUsers = allUsers.filter(function(user) {
        var matchesSearch = user.name.toLowerCase().includes(searchTerm) ||
                                    user.email.toLowerCase().includes(searchTerm) ||
                                    user.userid.toLowerCase().includes(searchTerm);
        var matchesStatus = selectedStatus === '' || user.status === selectedStatus;
        return matchesSearch && matchesStatus;
    });

    filteredUsers.forEach(function(user) {
        var row = document.createElement('tr');

        var UserIDCell = document.createElement('td');
        UserIDCell.textContent = user.userid;
        row.appendChild(UserIDCell);

        var nameCell = document.createElement('td');
        nameCell.textContent = user.name;
        row.appendChild(nameCell);

        var emailCell = document.createElement('td');
        emailCell.textContent = user.email;
        row.appendChild(emailCell);

        var statusCell = document.createElement('td');
        statusCell.textContent = user.status;
        row.appendChild(statusCell);

        var actionsCell = document.createElement('td');

        var userStatusBtn = document.createElement('button');
        userStatusBtn.textContent = user.status === 'active' ? 'Deactivate' : 'Activate';
        userStatusBtn.addEventListener('click', function() {
            if (user.status === 'active') {
                user.status = 'deactivated';
                userStatusBtn.textContent = 'Activate';
            }
            else {
                user.status = 'active';
                userStatusBtn.textContent = 'Deactivate';
            }

    // Optional: re-render the list so the status column updates too
    renderUserList();
});

        actionsCell.appendChild(userStatusBtn);

        row.appendChild(actionsCell);

        userTableBody.appendChild(row);
    });
}

document.getElementById('search-input').addEventListener('input', function() {
    searchTerm = this.value.toLowerCase();
    renderUserList();
});

document.getElementById('status-filter').addEventListener('change', function() {
    selectedStatus = this.value;
    renderUserList();
});

renderUserList();