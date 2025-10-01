# EmailUser.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    
    # Format the subject with sender name and FinKin prefix
    formatted_subject = f"{sender_name} via FinKin - {subject_line}"
    
    # Create the email message
    message = Mail(
        from_email=from_address,
        to_emails=receiver_email,
        subject=formatted_subject,
        html_content=body
    )
    
    # Set the reply-to address to the sender's email
    message.reply_to = sender_email
    
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
