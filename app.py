from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from CreateNewUser import create_new_user, validate_user_input

# Load environment variables from ..env file
load_dotenv()

app = Flask(__name__, static_folder='frontend')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # For flash messages

@app.route('/')
def index():
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
    return render_template('ForgotPassword.html')

@app.route("/Home")
def home():
    return render_template('Home.html')
@app.route("/Users")
def users():
    return render_template('Users.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
