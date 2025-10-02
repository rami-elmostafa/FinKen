from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import os
from dotenv import load_dotenv
from CreateNewUser import create_new_user, validate_user_input
from SignInUser import sign_in_user, validate_sign_in_input
from FinishSignUp import get_signup_context, finalize_signup
from ProfilePictureHandler import save_user_profile_picture, get_user_profile_picture
from AdminManagement import (
    get_pending_registration_requests, 
    get_all_registration_requests,
    approve_registration_request,
    reject_registration_request,
    get_registration_request_details
)
from UserManagement import get_users_paginated, update_user_status, get_user_by_id, get_expiring_passwords, get_all_roles
from UpdateUser import update_user
from EmailUser import send_email

# Load environment variables from ..env file
load_dotenv()

app = Flask(__name__, static_folder='frontend')
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # For flash messages

def get_user_context():
    """Helper function to get user context for templates"""
    if 'user_id' not in session:
        return {}
    
    # Get user profile picture
    profile_result = get_user_profile_picture(session.get('user_id'))
    profile_picture = 'default_profile.webp'  # Default fallback
    if profile_result.get('success') and profile_result.get('profile_picture'):
        profile_picture = profile_result.get('profile_picture')
    
    return {
        'user_name': session.get('username'),  # Use username instead of full name
        'user_role': session.get('user_role'),
        'user_profile_picture': profile_picture
    }

@app.route('/profile_images/<filename>')
def profile_image(filename):
    """Serve profile images from the profile_images directory"""
    try:
        return send_from_directory('profile_images', filename)
    except FileNotFoundError:
        # If the requested file doesn't exist, serve the default profile picture
        return send_from_directory('profile_images', 'default_profile.webp')

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
            
            # All users go to the Home page regardless of role
            return redirect(url_for('home'))
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
        return redirect(url_for('index'))
    
    # Get pending registration requests for the admin dashboard
    pending_requests = get_pending_registration_requests()
    
    return render_template('AdminDashboard.html', 
                         user_name=session.get('user_name'),
                         pending_requests=pending_requests.get('requests', []))

@app.route('/ManageRegistrations')
def manage_registrations():
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    # Get paginated registration requests
    result = get_all_registration_requests(
        page=page, 
        per_page=20, 
        search_term=search_term, 
        status_filter=status_filter
    )
    
    user_context = get_user_context()
    return render_template('ManageRegistrations.html', 
                         requests=result.get('requests', []),
                         pagination=result.get('pagination', {}),
                         current_search=search_term,
                         current_status=status_filter,
                         **user_context)

@app.route('/ApproveRegistration/<int:request_id>', methods=['POST'])
def approve_registration(request_id):
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('index'))
    
    reviewer_user_id = session.get('user_id')
    
    # Approve the registration request and send invitation email
    result = approve_registration_request(request_id, reviewer_user_id)
    
    if result.get('success'):
        flash(f'Registration request approved successfully. Invitation email sent.', 'success')
    else:
        flash(f'Failed to approve registration: {result.get("message", "Unknown error")}', 'error')
    
    return redirect(url_for('manage_registrations'))

@app.route('/RejectRegistration/<int:request_id>', methods=['POST'])
def reject_registration(request_id):
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('index'))
    
    reviewer_user_id = session.get('user_id')
    rejection_reason = request.form.get('rejection_reason', '')
    
    # Reject the registration request
    result = reject_registration_request(request_id, reviewer_user_id, rejection_reason)
    
    if result.get('success'):
        flash('Registration request rejected successfully.', 'success')
    else:
        flash(f'Failed to reject registration: {result.get("message", "Unknown error")}', 'error')
    
    return redirect(url_for('manage_registrations'))

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
        
        # Convert question_id to int safely
        try:
            question_id_int = int(question_id) if question_id and question_id.strip() else None
        except (ValueError, TypeError):
            question_id_int = None
        
        # Handle the signup process
        try:
            res = finalize_signup(token, password, confirm_password, question_id_int, answer)
        except Exception as e:
            print(f"Error in finalize_signup: {str(e)}")
            flash(f'Account creation failed: {str(e)}', 'error')
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
        
        if res.get('success'):
            # Handle profile picture upload if provided
            if 'profile_picture' in request.files:
                profile_file = request.files['profile_picture']
                if profile_file and profile_file.filename != '':
                    # Check file extension
                    allowed_extensions = {'.jpg', '.jpeg', '.png'}
                    file_ext = os.path.splitext(profile_file.filename.lower())[1]
                    if file_ext in allowed_extensions:
                        try:
                            # Get user_id from the signup result
                            user_id = res.get('user_id')
                            if user_id:
                                pic_result = save_user_profile_picture(user_id, profile_file)
                                if not pic_result.get('success'):
                                    flash(f'Account created but profile picture upload failed: {pic_result.get("message", "Unknown error")}', 'warning')
                        except Exception as e:
                            flash(f'Account created but profile picture upload failed: {str(e)}', 'warning')
            
            flash(f"Account created successfully! Your username is {res.get('username')}. Please sign in.", 'success')
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
    if 'user_id' not in session:
        flash('Please sign in to access this page.', 'error')
        return redirect(url_for('index'))
    
    user_context = get_user_context()
    return render_template('Home.html', **user_context)
@app.route("/Users")
def users():
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('index'))
    
    user_context = get_user_context()
    return render_template('Users.html', **user_context)

@app.route('/ExpiringPasswords')
def expiring_passwords():
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        flash('Access denied. Administrator privileges required.', 'error')
        return redirect(url_for('index'))
    
    # Get users with passwords expiring in the next 30 days
    result = get_expiring_passwords(days_ahead=30)
    
    user_context = get_user_context()
    return render_template('ExpiringPasswords.html', 
                         users=result.get('users', []),
                         total_count=result.get('total_count', 0),
                         **user_context)

@app.route('/api/users')
def api_users():
    """API endpoint to get paginated users data"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search', '', type=str)
    status_filter = request.args.get('status', '', type=str)
    
    # Get paginated users
    result = get_users_paginated(
        page=page, 
        per_page=20, 
        search_term=search_term, 
        status_filter=status_filter
    )
    
    return jsonify(result)

@app.route('/api/users/<int:user_id>/status', methods=['POST'])
def update_user_status_api(user_id):
    """API endpoint to update user status"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    data = request.get_json()
    action = data.get('action')
    
    if action not in ['activate', 'deactivate', 'suspend', 'unsuspend']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    result = update_user_status(user_id, action)
    return jsonify(result)

@app.route('/api/send-email', methods=['POST'])
def send_email_api():
    """API endpoint to send email to users"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        # Get sender info from session
        sender_name = session.get('user_name', 'Administrator')
        
        # Extract form data
        recipient_email = data.get('recipient_email')
        subject = data.get('subject')
        message = data.get('message')
        
        if not all([recipient_email, subject, message]):
            return jsonify({
                'success': False, 
                'message': 'Missing required fields: recipient_email, subject, or message'
            }), 400
        
        # Send the email
        result = send_email(
            sender_email='notifications@job-fit-ai.com',  # This will be set as reply-to
            sender_name=sender_name,
            receiver_email=recipient_email,
            subject_line=subject,
            body=message
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error sending email: {str(e)}'
        }), 500

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_details_api(user_id):
    """API endpoint to get detailed user information for editing"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = get_user_by_id(user_id)
    return jsonify(result)

@app.route('/api/roles', methods=['GET'])
def get_roles_api():
    """API endpoint to get all available roles"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    result = get_all_roles()
    return jsonify(result)

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_api(user_id):
    """API endpoint to update user information"""
    if 'user_id' not in session or session.get('user_role') != 'administrator':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Extract user data from request
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        dob = data.get('dob')
        address = data.get('address')
        role_id = data.get('role_id')
        
        # Convert empty strings to None for optional fields
        if dob == '':
            dob = None
        if address == '':
            address = None
        if role_id == '' or role_id == 'null':
            role_id = None
        
        # Convert role_id to int if provided
        if role_id is not None:
            try:
                role_id = int(role_id)
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': 'Invalid role ID'
                }), 400
        
        # Validate required fields
        if not first_name or not last_name or not email:
            return jsonify({
                'success': False,
                'message': 'First name, last name, and email are required'
            }), 400
        
        # Update the user
        result = update_user(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            dob=dob,
            address=address,
            roleid=role_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating user: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)
