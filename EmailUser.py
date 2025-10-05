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
