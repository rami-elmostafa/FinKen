# Password Expiry Notification Setup Guide

This guide explains how to set up automated password expiry notifications for the FinKen application.

## Overview

The system will automatically send email notifications to users whose passwords are expiring within 3 days. The notifications are sent daily at 9:00 AM UTC.

## Components Added

### 1. Email Function (`EmailUser.py`)
- `send_password_expiry_notifications()`: Main function that identifies users with expiring passwords and sends them email notifications

### 2. API Routes (`app.py`)
- `/api/send-password-expiry-notifications` (POST): Manual trigger for administrators
- `/cron/password-expiry-check` (GET): Automated endpoint for cron jobs

### 3. Supabase Cron Job (`supabase_cron_job.sql`)
- Database cron job that calls the Flask app endpoint daily
- Includes logging for monitoring and debugging

## Setup Instructions

### Step 1: Deploy the Code Changes
1. The code changes have been made to `EmailUser.py` and `app.py`
2. Deploy these changes to your production environment
3. Make sure your Flask app is running and accessible

### Step 2: Configure the Cron Job in Supabase

1. **Open Supabase SQL Editor**:
   - Go to your Supabase dashboard
   - Navigate to "SQL Editor"

2. **Update the App URL**:
   - Open the `supabase_cron_job.sql` file
   - Replace `YOUR_APP_URL` with your actual Flask app URL (e.g., `https://your-app.herokuapp.com` or your domain)
   - Example: Change `YOUR_APP_URL/cron/password-expiry-check` to `https://finken-app.herokuapp.com/cron/password-expiry-check`

3. **Run the SQL Script**:
   - Copy the contents of `supabase_cron_job.sql`
   - Paste it into the Supabase SQL Editor
   - Execute the script

### Step 3: Verify the Setup

1. **Check Scheduled Jobs**:
   ```sql
   SELECT * FROM cron.job WHERE jobname LIKE '%password-expiry%';
   ```

2. **Test the Endpoint Manually**:
   - Visit: `https://your-app-url.com/cron/password-expiry-check`
   - You should see a JSON response indicating success or failure

3. **Monitor Logs**:
   ```sql
   SELECT * FROM public.cron_job_logs ORDER BY execution_time DESC LIMIT 10;
   ```

## How It Works

### 1. Daily Execution
- Every day at 9:00 AM UTC, Supabase triggers the cron job
- The cron job makes an HTTP request to your Flask app

### 2. User Identification
- The system queries for users with passwords expiring within 3 days
- Only active, non-suspended users are included

### 3. Email Notifications
- Personalized emails are sent to each user
- Email content varies based on urgency (expires today, tomorrow, or in X days)
- Emails include security tips and instructions for changing passwords

### 4. Response Logging
- All cron job executions are logged in the `cron_job_logs` table
- Logs include status, response body, and timestamps for monitoring

## Email Content Features

The password expiry emails include:
- **Personalized greeting** with user's first name
- **Urgency indicators** with color-coded warnings
- **Account information** (username, email, expiry date)
- **Step-by-step instructions** for changing passwords
- **Security tips** for creating strong passwords
- **Professional styling** with responsive design

## Monitoring and Troubleshooting

### Check Cron Job Status
```sql
-- View all scheduled cron jobs
SELECT * FROM cron.job;

-- View recent execution logs
SELECT * FROM public.cron_job_logs 
ORDER BY execution_time DESC 
LIMIT 20;
```

### Manual Testing
You can manually trigger the notifications:

1. **As an Administrator** (through the web interface):
   - Make a POST request to `/api/send-password-expiry-notifications`

2. **Direct Cron Endpoint** (for testing):
   - Visit `/cron/password-expiry-check` in your browser

### Common Issues and Solutions

1. **Cron job not running**:
   - Verify pg_cron extension is enabled in Supabase
   - Check that the app URL is correct and accessible
   - Ensure your app is not requiring authentication for the cron endpoint

2. **Emails not sending**:
   - Verify SendGrid API key is set in environment variables
   - Check that sender email is verified in SendGrid
   - Review the cron job logs for error messages

3. **Wrong users being notified**:
   - Verify password expiry dates are set correctly in the database
   - Check the user status filters (active, not suspended)

## Customization Options

### Change Notification Timing
To change when notifications are sent, modify the cron expression:
- `0 9 * * *` = 9:00 AM UTC daily
- `0 8 * * 1-5` = 8:00 AM UTC on weekdays only
- `0 */6 * * *` = Every 6 hours

### Change Advance Notice Period
To change the 3-day advance notice:
1. Modify the `days_ahead` parameter in the cron job URL:
   ```
   YOUR_APP_URL/cron/password-expiry-check?days=5
   ```
2. Update the function to accept query parameters (optional enhancement)

### Customize Email Content
Edit the `send_password_expiry_notifications()` function in `EmailUser.py` to:
- Change email styling
- Modify the message content
- Add company branding
- Include additional security information

## Security Considerations

1. **Endpoint Security**: The cron endpoint doesn't require authentication to allow automated access
2. **Email Content**: Emails don't include sensitive information like actual passwords
3. **Logging**: Response logs may contain user information - ensure proper access controls
4. **Rate Limiting**: Consider implementing rate limiting if the endpoint might be abused

## Next Steps

After setup, consider:
1. Adding email templates for different languages
2. Implementing user preferences for notification timing
3. Adding SMS notifications as an alternative
4. Creating a dashboard for administrators to monitor password expiry trends