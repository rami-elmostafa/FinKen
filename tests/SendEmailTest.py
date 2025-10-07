# SendEmailTest.py

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv  # <-- 1. IMPORT the library

load_dotenv()  # <-- 2. LOAD the ..env file

# 3. USE YOUR VERIFIED DOMAIN in the from_email
#    This must be an address from the domain you authenticated (job-fit-ai.com)
#    It does not need to be a real inbox, just use the domain.
from_address = 'notifications@job-fit-ai.com' 

message = Mail(
    from_email=from_address,
    to_emails='ethanbradforddillon@gmail.com', # The recipient can be anyone
    subject='Sending with Twilio SendGrid is Fun',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')

try:
    # This will now correctly load your key from the ..env file
    api_key = os.environ.get('SENDGRID_API_KEY')
    sg = SendGridAPIClient(api_key)
    
    response = sg.send(message)
    
    # Print the results if successful
    print(f"Status Code: {response.status_code}")
    print("Email sent successfully!")

except Exception as e:
    # 4. FIX the error printing
    print("An error occurred:")
    print(e)