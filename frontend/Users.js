let currentPage = 1;
let currentSearch = '';
let currentStatus = '';

// Load users function
async function loadUsers(page = 1, search = '', status = '') {
    try {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('no-users').style.display = 'none';
        
        const params = new URLSearchParams({
            page: page,
            search: search,
            status: status
        });
        
        const response = await fetch(`/api/users?${params}`);
        const data = await response.json();
        
        document.getElementById('loading').style.display = 'none';
        
        if (data.success) {
            renderUsers(data.users);
            renderPagination(data.pagination);
        } else {
            console.error('Error loading users:', data.message);
            document.getElementById('no-users').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading users:', error);
        document.getElementById('loading').style.display = 'none';
        document.getElementById('no-users').style.display = 'block';
    }
}

// Render users in table
function renderUsers(users) {
    const tbody = document.getElementById('users-table-body');
    tbody.innerHTML = '';
    
    if (users.length === 0) {
        document.getElementById('no-users').style.display = 'block';
        return;
    }
    
    users.forEach(user => {
        const row = document.createElement('tr');
        
        const statusBadgeClass = `status-${user.Status.toLowerCase()}`;
        const actionButtons = createActionButtons(user);
        
        row.innerHTML = `
            <td>${user.UserID}</td>
            <td>${user.Username || 'N/A'}</td>
            <td>${user.FirstName} ${user.LastName}</td>
            <td>${user.Email}</td>
            <td>${user.DOB || 'N/A'}</td>
            <td>${user.Address || 'N/A'}</td>
            <td>${user.RoleName}</td>
            <td><span class="status-badge ${statusBadgeClass}">${user.Status}</span></td>
            <td>${user.DateCreated ? user.DateCreated.substring(0, 10) : 'N/A'}</td>
            <td>${actionButtons}</td>
        `;
        
        tbody.appendChild(row);
    });
    
    // Attach event listeners to action buttons
    attachActionListeners();
}

// Create action buttons for each user
function createActionButtons(user) {
    let buttons = `<div class="action-buttons">`;
    
    // Edit button (only for admins)
    buttons += `<button type="button" class="btn btn-small btn-secondary edit-btn" 
                data-user-id="${user.UserID}" 
                data-user-name="${user.FirstName} ${user.LastName}">Edit</button>`;
    
    // Email button
    buttons += `<button type="button" class="btn btn-small btn-primary email-btn" 
                data-user-id="${user.UserID}" 
                data-email="${user.Email}" 
                data-name="${user.FirstName} ${user.LastName}">Email</button>`;
    
    // Status buttons
    if (user.Status === 'active') {
        buttons += `<button type="button" class="btn btn-small btn-warning status-btn" 
                    data-user-id="${user.UserID}" 
                    data-action="suspend">Suspend</button>`;
        buttons += `<button type="button" class="btn btn-small btn-danger status-btn" 
                    data-user-id="${user.UserID}" 
                    data-action="deactivate">Deactivate</button>`;
    } else if (user.Status === 'inactive') {
        buttons += `<button type="button" class="btn btn-small btn-success status-btn" 
                    data-user-id="${user.UserID}" 
                    data-action="activate">Activate</button>`;
    } else if (user.Status === 'suspended') {
        buttons += `<button type="button" class="btn btn-small btn-success status-btn" 
                    data-user-id="${user.UserID}" 
                    data-action="unsuspend">Unsuspend</button>`;
    }
    
    buttons += `</div>`;
    return buttons;
}

// Attach event listeners to action buttons
function attachActionListeners() {
    // Edit buttons
    document.querySelectorAll('.edit-btn').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const userName = this.dataset.userName;
            showEditModal(userId, userName);
        });
    });
    
    // Email buttons
    document.querySelectorAll('.email-btn').forEach(button => {
        button.addEventListener('click', function() {
            const email = this.dataset.email;
            const name = this.dataset.name;
            showEmailModal(email, name);
        });
    });
    
    // Status buttons
    document.querySelectorAll('.status-btn').forEach(button => {
        button.addEventListener('click', async function() {
            const userId = this.dataset.userId;
            const action = this.dataset.action;
            
            if (confirm(`Are you sure you want to ${action} this user?`)) {
                await updateUserStatus(userId, action);
            }
        });
    });
}

// Update user status
async function updateUserStatus(userId, action) {
    try {
        const response = await fetch(`/api/users/${userId}/status`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: action })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Reload current page
            loadUsers(currentPage, currentSearch, currentStatus);
        } else {
            alert('Error updating user status: ' + data.message);
        }
    } catch (error) {
        console.error('Error updating user status:', error);
        alert('Error updating user status');
    }
}

// Render pagination
function renderPagination(pagination) {
    const paginationDiv = document.getElementById('pagination');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    if (pagination.total_pages <= 1) {
        paginationDiv.style.display = 'none';
        return;
    }
    
    paginationDiv.style.display = 'flex';
    
    prevBtn.disabled = !pagination.has_prev;
    nextBtn.disabled = !pagination.has_next;
    
    pageInfo.textContent = `Page ${pagination.current_page} of ${pagination.total_pages} (${pagination.total_users} total users)`;
    
    // Update current page
    currentPage = pagination.current_page;
}

// Edit modal functions
let rolesLoaded = false;
let availableRoles = [];

async function loadRoles() {
    if (rolesLoaded) return;
    
    try {
        const response = await fetch('/api/roles');
        const data = await response.json();
        
        if (data.success) {
            availableRoles = data.roles;
            rolesLoaded = true;
            populateRoleSelect();
        } else {
            console.error('Error loading roles:', data.message);
        }
    } catch (error) {
        console.error('Error loading roles:', error);
    }
}

function populateRoleSelect() {
    const select = document.getElementById('edit-role');
    select.innerHTML = '<option value="">Select a role...</option>';
    
    availableRoles.forEach(role => {
        const option = document.createElement('option');
        option.value = role.RoleID;
        option.textContent = role.RoleName;
        select.appendChild(option);
    });
}

async function showEditModal(userId, userName) {
    // Load roles if not already loaded
    await loadRoles();
    
    try {
        // Fetch user data
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        
        if (data.success) {
            const user = data.user;
            
            // Populate form fields
            document.getElementById('edit-user-id').value = user.UserID;
            document.getElementById('edit-first-name').value = user.FirstName || '';
            document.getElementById('edit-last-name').value = user.LastName || '';
            document.getElementById('edit-email').value = user.Email || '';
            document.getElementById('edit-dob').value = user.DOB || '';
            document.getElementById('edit-address').value = user.Address || '';
            
            // Set role selection
            const roleSelect = document.getElementById('edit-role');
            if (user.RoleID) {
                roleSelect.value = user.RoleID;
            } else {
                // Fallback: try to find by role name
                const userRole = availableRoles.find(role => role.RoleName === user.RoleName);
                if (userRole) {
                    roleSelect.value = userRole.RoleID;
                }
            }
            
            // Show modal
            document.getElementById('edit-modal').style.display = 'block';
        } else {
            alert('Error loading user data: ' + data.message);
        }
    } catch (error) {
        console.error('Error loading user data:', error);
        alert('Error loading user data');
    }
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// Email modal functions
function showEmailModal(email, name) {
    document.getElementById('email-recipient').value = email;
    document.getElementById('email-subject').value = '';
    document.getElementById('email-message').value = '';
    document.getElementById('email-modal').style.display = 'block';
}

function closeEmailModal() {
    document.getElementById('email-modal').style.display = 'none';
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Load initial users
    loadUsers();
    
    // Search functionality
    document.getElementById('search-input').addEventListener('input', function() {
        currentSearch = this.value;
        currentPage = 1;
        loadUsers(currentPage, currentSearch, currentStatus);
    });
    
    // Status filter
    document.getElementById('status-filter').addEventListener('change', function() {
        currentStatus = this.value;
        currentPage = 1;
        loadUsers(currentPage, currentSearch, currentStatus);
    });
    
    // Pagination buttons
    document.getElementById('prev-page').addEventListener('click', function() {
        if (currentPage > 1) {
            loadUsers(currentPage - 1, currentSearch, currentStatus);
        }
    });
    
    document.getElementById('next-page').addEventListener('click', function() {
        loadUsers(currentPage + 1, currentSearch, currentStatus);
    });
    
    // Email modal events
    document.getElementById('close-email-modal').addEventListener('click', closeEmailModal);
    document.getElementById('cancel-email').addEventListener('click', closeEmailModal);
    
    // Edit modal events
    document.getElementById('close-edit-modal').addEventListener('click', closeEditModal);
    document.getElementById('cancel-edit').addEventListener('click', closeEditModal);
    
    // Edit form submission
    document.getElementById('edit-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const userId = formData.get('user_id');
        const data = {
            first_name: formData.get('first_name'),
            last_name: formData.get('last_name'),
            email: formData.get('email'),
            dob: formData.get('dob') || null,
            address: formData.get('address') || null,
            role_id: formData.get('role_id') || null
        };
        
        console.log('Sending data:', data); // Debug log
        
        try {
            const response = await fetch(`/api/users/${userId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            console.log('Response status:', response.status); // Debug log
            
            const result = await response.json();
            console.log('Response data:', result); // Debug log
            
            if (result.success) {
                alert('User updated successfully!');
                closeEditModal();
                // Reload current page to show updated data
                loadUsers(currentPage, currentSearch, currentStatus);
            } else {
                alert('Error updating user: ' + (result.message || 'Unknown error'));
            }
        } catch (error) {
            console.error('Error updating user:', error);
            alert('Error updating user: ' + error.message);
        }
    });
    
    // Email form submission
    document.getElementById('email-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = {
            recipient_email: formData.get('recipient_email'),
            subject: formData.get('subject'),
            message: formData.get('message')
        };
        
        try {
            const response = await fetch('/api/send-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                alert('Email sent successfully!');
                closeEmailModal();
            } else {
                alert('Error sending email: ' + result.message);
            }
        } catch (error) {
            console.error('Error sending email:', error);
            alert('Error sending email');
        }
    });
});

// Navigation
document.querySelector('.nav-toggle').addEventListener('click', function() {
    document.querySelector('.navbar').style.left = '0';
});

document.querySelector('.navbar').addEventListener('mouseleave', function() {
    document.querySelector('.navbar').style.left = '-250px';
});

// Close modal when clicking outside
window.onclick = function(event) {
    const emailModal = document.getElementById('email-modal');
    const editModal = document.getElementById('edit-modal');
    
    if (event.target === emailModal) {
        closeEmailModal();
    } else if (event.target === editModal) {
        closeEditModal();
    }
}