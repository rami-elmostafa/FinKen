// Password validation and real-time feedback
function validatePassword(password) {
    const errors = [];
    
    if (password.length < 8) {
        errors.push("Password must be at least 8 characters long");
    }
    
    if (password.length > 0 && !password[0].match(/[a-zA-Z]/)) {
        errors.push("Password must start with a letter");
    }
    
    if (!/[a-zA-Z]/.test(password)) {
        errors.push("Password must contain at least one letter");
    }
    
    if (!/[0-9]/.test(password)) {
        errors.push("Password must contain at least one number");
    }
    
    if (!/[^a-zA-Z0-9]/.test(password)) {
        errors.push("Password must contain at least one special character");
    }
    
    return {
        valid: errors.length === 0,
        errors: errors
    };
}

// Real-time password validation
function setupPasswordValidation() {
    const passwordField = document.getElementById('password');
    if (!passwordField) return;
    
    passwordField.addEventListener('input', function() {
        const password = this.value;
        const requirements = document.querySelector('.password-requirements');
        
        if (!requirements) return;
        
        if (password.length === 0) {
            requirements.style.color = '#666';
            requirements.textContent = 'Password must be at least 8 characters, start with a letter, and include a letter, number, and special character';
            return;
        }
        
        const validation = validatePassword(password);
        
        if (validation.valid) {
            requirements.style.color = 'green';
            requirements.textContent = '✓ Password meets all requirements';
        } else {
            requirements.style.color = 'red';
            requirements.textContent = validation.errors.join('. ');
        }
    });
}

// Password confirmation validation
function checkPasswordMatch() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password') || document.getElementById('confirm');
    const messageDiv = document.getElementById('password-match-message');
    
    if (!password || !confirmPassword || !messageDiv) return;
    
    const confirmValue = confirmPassword.value;
    
    if (confirmValue.length === 0) {
        messageDiv.textContent = '';
        return;
    }
    
    if (password.value === confirmValue) {
        messageDiv.style.color = 'green';
        messageDiv.textContent = '✓ Passwords match';
    } else {
        messageDiv.style.color = 'red';
        messageDiv.textContent = '✗ Passwords do not match';
    }
}

// Setup password confirmation validation
function setupPasswordConfirmation() {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password') || document.getElementById('confirm');
    
    if (password && confirmPassword) {
        confirmPassword.addEventListener('input', checkPasswordMatch);
        password.addEventListener('input', checkPasswordMatch);
    }
}

// Form submission validation for reset password
function setupResetPasswordFormValidation() {
    const form = document.querySelector('form');
    if (!form) return;
    
    // Check if this is the reset password form
    if (form.action.includes('reset_password')) {
        form.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm').value;
            
            // Validate password
            const validation = validatePassword(password);
            if (!validation.valid) {
                alert('Password does not meet requirements:\n' + validation.errors.join('\n'));
                e.preventDefault();
                return;
            }
            
            // Check password match
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                e.preventDefault();
                return;
            }
            
            // Disable submit button to prevent double submission
            const submitBtn = document.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Resetting Password...';
            }
        });
    }
}

// Form submission validation for finish signup
function setupFinishSignupFormValidation() {
    const form = document.getElementById('finish-signup-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        const securityQuestion = document.getElementById('security_question').value;
        const securityAnswer = document.getElementById('security_answer').value.trim();
        
        // Validate password
        const validation = validatePassword(password);
        if (!validation.valid) {
            alert('Password does not meet requirements:\n' + validation.errors.join('\n'));
            e.preventDefault();
            return;
        }
        
        // Check password match
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            e.preventDefault();
            return;
        }
        
        // Check security question and answer
        if (!securityQuestion) {
            alert('Please select a security question');
            e.preventDefault();
            return;
        }
        
        if (!securityAnswer) {
            alert('Please provide an answer to your security question');
            e.preventDefault();
            return;
        }
        
        // Disable submit button to prevent double submission
        const submitBtn = document.getElementById('submit-btn');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating Account...';
        }
    });
}

// Initialize all password validation functionality
function initializePasswordValidation() {
    // Wait for DOM to be fully loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setupPasswordValidation();
            setupPasswordConfirmation();
            setupResetPasswordFormValidation();
            setupFinishSignupFormValidation();
        });
    } else {
        setupPasswordValidation();
        setupPasswordConfirmation();
        setupResetPasswordFormValidation();
        setupFinishSignupFormValidation();
    }
}

// Initialize when script loads
initializePasswordValidation();