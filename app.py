from flask import Flask, render_template, request, redirect, url_for, flash, session
import os
from dotenv import load_dotenv
from CreateNewUser import create_new_user, validate_user_input
from SignInUser import sign_in_user, validate_sign_in_input
from FinishSignUp import get_signup_context, finalize_signup

# Load environment variables from ..env file
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
            role = (result['user_data'].get('role') or '').strip().lower() or 'accountant'
            session['user_role'] = role
            session['user_name'] = f"{result['user_data']['first_name']} {result['user_data']['last_name']}"
            
            flash(f'Welcome back, {result["user_data"]["first_name"]}!', 'success')
            
            # Redirect based on user role
            if role == 'administrator':
                return redirect(url_for('admin_dashboard'))
            elif role == 'manager':
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
        address = request.form.get('address')
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
            first_name, last_name, email, dob, address
        )
        
        if result['success']:
            flash('Your user request has been submitted and is awaiting approval!', 'success')
            return redirect(url_for('index'))
        else:
            flash(f'Registration failed: {result["message"]}', 'error')
            return render_template('CreateNewUser.html')

@app.route("/ForgotPassword")
def forgot_password():
    return render_template('ForgotPassword.html')

@app.route('/SignOut')
def sign_out():
    # Clear the session
    session.clear()
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('index'))

# Placeholder routes for different user dashboards
@app.route('/AdminDashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('sign_in'))
    return f"Admin Dashboard - Welcome {session.get('user_name')}"

@app.route('/ManagerDashboard')
def manager_dashboard():
    if 'user_id' not in session or session.get('user_role') not in ['administrator', 'manager']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('sign_in'))
    return f"Manager Dashboard - Welcome {session.get('user_name')}"

@app.route('/AccountantDashboard')
def accountant_dashboard():
    if 'user_id' not in session:
        flash('Please sign in to access this page.', 'error')
        return redirect(url_for('sign_in'))
    return f"Accountant Dashboard - Welcome {session.get('user_name')}"

@app.route('/FinishSignUp', methods=['GET', 'POST'])
def finish_sign_up():
    if request.method == 'GET':
        token = request.args.get('token')
        if not token:
            flash('Missing signup token.', 'error')
            return redirect(url_for('index'))
        ctx = get_signup_context(token)
        if not ctx.get('success'):
            flash(ctx.get('message', 'Invalid signup link'), 'error')
            return redirect(url_for('index'))
        full_name = f"{ctx['request'].get('FirstName','')} {ctx['request'].get('LastName','')}".strip()
        return render_template('FinishSignUp.html',
                               token=token,
                               full_name=full_name,
                               security_questions=ctx.get('security_questions', []))
    else:
        token = request.form.get('token')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        question_id = request.form.get('security_question')
        answer = request.form.get('security_answer')
        res = finalize_signup(token, password, confirm_password, int(question_id) if question_id else None, answer)
        if res.get('success'):
            flash(f"Account created. Your username is {res.get('username')}. Please sign in.", 'success')
            return redirect(url_for('index'))
        else:
            flash(res.get('message', 'Could not complete sign up'), 'error')
            # Re-hydrate page with questions again
            ctx = get_signup_context(token)
            full_name = ''
            questions = []
            if ctx.get('success'):
                full_name = f"{ctx['request'].get('FirstName','')} {ctx['request'].get('LastName','')}".strip()
                questions = ctx.get('security_questions', [])
            return render_template('FinishSignUp.html',
                                   token=token,
                                   full_name=full_name,
                                   security_questions=questions)
        
        
@app.route("/Home")
def home():
    return render_template('Home.html')
@app.route("/Users")
def users():
    return render_template('Users.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
