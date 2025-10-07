# EmailUser.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from SupabaseClient import _sb

def send_email(sender_email, sender_name, receiver_email, subject_line, body):
    """
    Send an email via SendGrid API
    
    Args:
        sender_email (str): The email address to set as reply-to
        sender_name (str): The name of the sender
        receiver_email (str): The recipient's email address
        subject_line (str): The original subject line
        body (str): The email body content (HTML or plain text)
    
    Returns:
        dict: Response containing status and message
    """
    
    # Always send from the verified domain
    from_address = 'notifications@job-fit-ai.com'
    
    # Format the subject with sender name and FinKen prefix
    formatted_subject = f"{sender_name} via FinKen - {subject_line}"
    
    # Create the email message
    message = Mail(
        from_email=from_address,
        to_emails=receiver_email,
        subject=formatted_subject,
        html_content=body
    )
    
    # Set the reply-to address to the sender's email
    message.reply_to = (sender_email, sender_name)
    
    try:
        # Get API key from environment variables
        api_key = os.environ.get('SENDGRID_API_KEY')
        
        if not api_key:
            return {
                'success': False,
                'error': 'SENDGRID_API_KEY not found in environment variables'
            }
        
        # Initialize SendGrid client and send email
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        return {
            'success': True,
            'status_code': response.status_code,
            'message': 'Email sent successfully!'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def NewUserAdminNotification(first_name, last_name, email, sb = None):
    """
    Send notification to all administrators about a new user registration request
    
    Args:
        first_name (str): The new user's first name
        last_name (str): The new user's last name
        email (str): The new user's email address
    
    Returns:
        dict: Response containing status and message
    """
    
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Query to get all administrators' emails
        # Join users table with roles table to get users with administrator role
        response = sb.table('users').select('Email, FirstName, LastName').eq('RoleID', 1).eq('IsActive', True).execute()
        
        if not response.data:
            return {
                'success': False,
                'error': 'No active administrators found in the system'
            }
        
        admin_emails = [admin['Email'] for admin in response.data if admin.get('Email')]
        
        if not admin_emails:
            return {
                'success': False,
                'error': 'No administrator email addresses found'
            }
        
        # Create email content
        full_name = f"{first_name} {last_name}"
        subject = "New User Registration Request - FinKen"
        
        # HTML email body
        email_body = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px;">
                New User Registration Request
            </h2>
            
            <p style="font-size: 16px; color: #555; margin: 20px 0;">
                A new user has submitted a registration request and is awaiting approval.
            </p>
            
            <div style="background-color: #f9f9f9; padding: 20px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">User Information:</h3>
                <p style="margin: 5px 0;"><strong>Name:</strong> {full_name}</p>
                <p style="margin: 5px 0;"><strong>Email:</strong> {email}</p>
            </div>
            
            <p style="font-size: 14px; color: #777; margin: 20px 0;">
                Please log into the FinKen admin panel to review and approve or reject this registration request.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="font-size: 12px; color: #999; text-align: center;">
                This is an automated notification from FinKen.<br>
                Please do not reply to this email.
            </p>
        </div>
        """
        
        # Send email to each administrator
        successful_sends = 0
        failed_sends = 0
        errors = []
        
        for admin_email in admin_emails:
            try:
                # Use the existing send_email function
                result = send_email(
                    sender_email='notifications@job-fit-ai.com',
                    sender_name='FinKen System',
                    receiver_email=admin_email,
                    subject_line=subject,
                    body=email_body
                )
                
                if result.get('success'):
                    successful_sends += 1
                else:
                    failed_sends += 1
                    errors.append(f"Failed to send to {admin_email}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                failed_sends += 1
                errors.append(f"Failed to send to {admin_email}: {str(e)}")
        
        # Return summary of results
        if successful_sends > 0 and failed_sends == 0:
            return {
                'success': True,
                'message': f'Successfully notified all {successful_sends} administrators about the new user registration request'
            }
        elif successful_sends > 0 and failed_sends > 0:
            return {
                'success': True,
                'message': f'Notified {successful_sends} administrators successfully, but {failed_sends} failed',
                'errors': errors
            }
        else:
            return {
                'success': False,
                'error': f'Failed to notify any administrators. Errors: {"; ".join(errors)}'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error sending admin notifications: {str(e)}'
        }

def send_password_expiry_notifications(sb=None):
    """
    Send email notifications to users whose passwords are expiring within 3 days
    
    Returns:
        dict: Response containing status and message with details about notifications sent
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Calculate the cutoff date (3 days from now)
        from datetime import datetime, timedelta, timezone
        cutoff_date = datetime.now(timezone.utc) + timedelta(days=3)
        cutoff_date_str = cutoff_date.isoformat()
        
        # Get users whose passwords expire within 3 days and are active
        response = sb.table('users').select(
            'UserID, Username, FirstName, LastName, Email, PasswordExpiryDate'
        ).lte('PasswordExpiryDate', cutoff_date_str).eq('IsActive', True).eq('IsSuspended', False).execute()
        
        if not response.data:
            return {
                'success': True,
                'message': 'No users with passwords expiring in the next 3 days',
                'users_notified': 0
            }
        
        successful_sends = 0
        failed_sends = 0
        errors = []
        notifications_sent = []
        
        for user in response.data:
            try:
                # Calculate days until expiry
                expiry_date = datetime.fromisoformat(user['PasswordExpiryDate'].replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                days_until_expiry = (expiry_date - now).days
                
                # Skip if password has already expired (negative days)
                if days_until_expiry < 0:
                    continue
                
                # Determine urgency level
                if days_until_expiry == 0:
                    urgency = "today"
                    urgency_color = "#dc3545"  # Red
                    urgency_message = "Your password expires today!"
                elif days_until_expiry == 1:
                    urgency = "tomorrow"
                    urgency_color = "#fd7e14"  # Orange
                    urgency_message = "Your password expires tomorrow!"
                else:
                    urgency = f"in {days_until_expiry} days"
                    urgency_color = "#ffc107"  # Yellow
                    urgency_message = f"Your password expires in {days_until_expiry} days."
                
                # Create personalized email content
                first_name = user.get('FirstName', 'User')
                username = user.get('Username', 'your username')
                email_address = user.get('Email')
                
                subject = f"Password Expiry Warning - Action Required"
                
                # HTML email body
                email_body = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background-color: #f8f9fa; padding: 20px;">
                    <div style="background-color: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h1 style="color: #333; margin: 0; font-size: 24px;">FinKen - Password Expiry Warning</h1>
                        </div>
                        
                        <!-- Urgency Alert -->
                        <div style="background-color: {urgency_color}; color: white; padding: 15px; border-radius: 6px; text-align: center; margin-bottom: 25px;">
                            <h2 style="margin: 0; font-size: 18px;">{urgency_message}</h2>
                        </div>
                        
                        <!-- Greeting -->
                        <p style="font-size: 16px; color: #333; margin-bottom: 20px;">
                            Hello {first_name},
                        </p>
                        
                        <!-- Main Message -->
                        <p style="font-size: 16px; color: #555; line-height: 1.6; margin-bottom: 20px;">
                            This is an automated reminder that your FinKen account password is set to expire <strong>{urgency}</strong>.
                        </p>
                        
                        <!-- Account Details -->
                        <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0;">
                            <h3 style="color: #333; margin-top: 0; font-size: 16px;">Account Information:</h3>
                            <p style="margin: 5px 0; color: #555;"><strong>Username:</strong> {username}</p>
                            <p style="margin: 5px 0; color: #555;"><strong>Email:</strong> {email_address}</p>
                            <p style="margin: 5px 0; color: #555;"><strong>Password Expires:</strong> {expiry_date.strftime('%B %d, %Y at %I:%M %p UTC')}</p>
                        </div>
                        
                        <!-- Action Required -->
                        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 20px; border-radius: 6px; margin: 20px 0;">
                            <h3 style="color: #856404; margin-top: 0; font-size: 16px;">Action Required:</h3>
                            <p style="color: #856404; margin: 5px 0; line-height: 1.6;">
                                To maintain access to your FinKen account, please log in and change your password before it expires. 
                                If your password expires, you may need to contact an administrator to regain access.
                            </p>
                        </div>
                        
                        <!-- Instructions -->
                        <div style="margin: 25px 0;">
                            <h3 style="color: #333; font-size: 16px;">How to Change Your Password:</h3>
                            <ol style="color: #555; line-height: 1.6; padding-left: 20px;">
                                <li>Log into your FinKen account</li>
                                <li>Navigate to your profile or account settings</li>
                                <li>Select "Change Password"</li>
                                <li>Enter your current password and choose a new secure password</li>
                                <li>Save your changes</li>
                            </ol>
                        </div>
                        
                        <!-- Security Tips -->
                        <div style="background-color: #e8f5e8; border: 1px solid #c3e6c3; padding: 15px; border-radius: 6px; margin: 20px 0;">
                            <h4 style="color: #2d5a2d; margin-top: 0; font-size: 14px;">💡 Password Security Tips:</h4>
                            <ul style="color: #2d5a2d; font-size: 14px; margin: 5px 0; padding-left: 20px; line-height: 1.5;">
                                <li>Use a combination of uppercase and lowercase letters, numbers, and special characters</li>
                                <li>Make your password at least 8 characters long</li>
                                <li>Avoid using personal information or common words</li>
                                <li>Consider using a password manager for stronger security</li>
                            </ul>
                        </div>
                        
                        <!-- Footer -->
                        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                        
                        <p style="font-size: 12px; color: #999; text-align: center; margin: 10px 0;">
                            This is an automated security notification from FinKen.<br>
                            Please do not reply to this email. If you need assistance, contact your system administrator.
                        </p>
                        
                        <p style="font-size: 11px; color: #ccc; text-align: center; margin: 0;">
                            FinKen Financial Management System<br>
                            Automated Password Management Service
                        </p>
                    </div>
                </div>
                """
                
                # Send the email
                result = send_email(
                    sender_email='notifications@job-fit-ai.com',
                    sender_name='FinKen Security',
                    receiver_email=email_address,
                    subject_line=subject,
                    body=email_body
                )
                
                if result.get('success'):
                    successful_sends += 1
                    notifications_sent.append({
                        'user_id': user['UserID'],
                        'name': first_name,
                        'email': email_address,
                        'days_until_expiry': days_until_expiry,
                        'expiry_date': user['PasswordExpiryDate']
                    })
                else:
                    failed_sends += 1
                    errors.append(f"Failed to send to {email_address}: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                failed_sends += 1
                errors.append(f"Failed to process user {user.get('UserID', 'unknown')}: {str(e)}")
        
        # Return summary of results
        if successful_sends > 0 and failed_sends == 0:
            return {
                'success': True,
                'message': f'Successfully sent password expiry notifications to {successful_sends} users',
                'users_notified': successful_sends,
                'notifications_sent': notifications_sent
            }
        elif successful_sends > 0 and failed_sends > 0:
            return {
                'success': True,
                'message': f'Sent notifications to {successful_sends} users successfully, but {failed_sends} failed',
                'users_notified': successful_sends,
                'notifications_sent': notifications_sent,
                'errors': errors
            }
        else:
            return {
                'success': False,
                'error': f'Failed to send notifications to any users. Errors: {"; ".join(errors)}',
                'users_notified': 0
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': f'Error sending password expiry notifications: {str(e)}',
            'users_notified': 0
        }
