from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from dotenv import load_dotenv
from CreateNewUser import create_new_user, validate_user_input
from SignInUser import sign_in_user, validate_sign_in_input

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_folder='frontend')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # For flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    
    elif request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        validation_result = validate_sign_in_input(username, password)
        
        if not validation_result['success']:
            flash(f'Sign in failed: {validation_result["message"]}', 'error')
            return render_template('index.html')
        
        # Attempt to sign in user
        result = sign_in_user(username, password)
        
        if result['success']:
            # Store user data in session
            session['user_id'] = result['user_data']['user_id']
            session['username'] = result['user_data']['username']
            session['user_role'] = result['user_data']['role']
            session['user_name'] = f"{result['user_data']['first_name']} {result['user_data']['last_name']}"
            
            flash(f'Welcome back, {result["user_data"]["first_name"]}!', 'success')
            
            # Redirect based on user role
            if result['user_data']['role'] == 'administrator':
                return redirect(url_for('admin_dashboard'))
            elif result['user_data']['role'] == 'manager':
                return redirect(url_for('manager_dashboard'))
            else:  # accountant or default role
                return redirect(url_for('accountant_dashboard'))
        else:
            flash(f'Sign in failed: {result["message"]}', 'error')
            return render_template('index.html')

@app.route('/CreateNewUser', methods=['GET', 'POST'])
def create_new_user_route():
    if request.method == 'GET':
        return render_template('CreateNewUser.html')
    
    elif request.method == 'POST':
        # Get form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        dob = request.form.get('dob')
        
        # Validate input
        validation_result = validate_user_input(
            first_name, last_name, email, dob
        )
        
        if not validation_result['success']:
            flash(f'Registration failed: {validation_result["message"]}', 'error')
            return render_template('CreateNewUser.html')
        
        # Create user
        result = create_new_user(
            first_name, last_name, email, dob
        )
        
        if result['success']:
            flash('Your user request has been submitted and is awaiting approval!', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Registration failed: {result["message"]}', 'error')
            return render_template('CreateNewUser.html')

@app.route("/ForgotPassword")
def forgot_password():
    # Change this to whatever the new forgot password page is once it is created
    return render_template('ForgotPassword.html')

@app.route('/SignOut')
def sign_out():
    # Clear the session
    session.clear()
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('index'))

# Placeholder routes for different user dashboards
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('sign_in'))
    return f"Admin Dashboard - Welcome {session.get('user_name')}"

@app.route('/manager_dashboard')
def manager_dashboard():
    if 'user_id' not in session or session.get('user_role') not in ['administrator', 'manager']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('sign_in'))
    return f"Manager Dashboard - Welcome {session.get('user_name')}"

@app.route('/accountant_dashboard')
def accountant_dashboard():
    if 'user_id' not in session:
        flash('Please sign in to access this page.', 'error')
        return redirect(url_for('sign_in'))
    return f"Accountant Dashboard - Welcome {session.get('user_name')}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
