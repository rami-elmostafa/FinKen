-- Supabase Cron Job for Password Expiry Notifications
-- This script sets up a cron job to check for expiring passwords daily and send notifications

-- First, make sure the pg_cron extension is enabled (Supabase should have this enabled)
-- If not enabled, you may need to contact Supabase support or enable it in your project settings

-- Drop the cron job if it already exists (for re-deployment)
SELECT cron.unschedule('password-expiry-notifications');

-- Schedule a daily cron job to run at 9:00 AM UTC every day
-- This will call your Flask app's cron endpoint to send password expiry notifications
SELECT cron.schedule(
    'password-expiry-notifications',  -- Job name
    '0 9 * * *',                     -- Cron expression: Run at 9:00 AM UTC daily
    $$
    SELECT
        net.http_post(
            url := 'https://finken.onrender.com/cron/password-expiry-check',
            headers := '{"Content-Type": "application/json"}'::jsonb
        ) as request_id;
    $$
);

-- Optional: Create a logging table to track cron job executions
CREATE TABLE IF NOT EXISTS public.cron_job_logs (
    id SERIAL PRIMARY KEY,
    job_name VARCHAR(100) NOT NULL,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,
    response_body TEXT,
    notes TEXT
);

-- Enable Row Level Security on the logging table
ALTER TABLE public.cron_job_logs ENABLE ROW LEVEL SECURITY;

-- Create a policy to allow service role to insert logs
CREATE POLICY "Allow service role to insert cron logs" 
ON public.cron_job_logs 
FOR INSERT 
TO service_role 
WITH CHECK (true);

-- Create a policy to allow authenticated users to read logs (for admin monitoring)
CREATE POLICY "Allow authenticated users to read cron logs" 
ON public.cron_job_logs 
FOR SELECT 
TO authenticated 
USING (true);

-- Enhanced cron job with logging
SELECT cron.schedule(
    'password-expiry-notifications-with-logging',
    '0 9 * * *',  -- Run at 9:00 AM UTC daily
    $$
    DO $$
    DECLARE
        response_record RECORD;
        status_code INTEGER;
        response_body TEXT;
    BEGIN
        -- Make the HTTP request to your Flask app
        SELECT 
            (response).status_code,
            (response).content::text
        INTO 
            status_code,
            response_body
        FROM 
            net.http_post(
                url := 'https://finken.onrender.com/cron/password-expiry-check',
                headers := '{"Content-Type": "application/json"}'::jsonb
            ) as response;
        
        -- Log the execution
        INSERT INTO public.cron_job_logs (job_name, status, response_body, notes)
        VALUES (
            'password-expiry-notifications',
            CASE 
                WHEN status_code = 200 THEN 'SUCCESS'
                ELSE 'FAILED'
            END,
            response_body,
            'Status Code: ' || status_code::text
        );
        
    EXCEPTION
        WHEN OTHERS THEN
            -- Log any errors
            INSERT INTO public.cron_job_logs (job_name, status, response_body, notes)
            VALUES (
                'password-expiry-notifications',
                'ERROR',
                NULL,
                'Error: ' || SQLERRM
            );
    END $$;
    $$
);

-- Query to check scheduled cron jobs
-- Run this to verify your cron job is scheduled:
-- SELECT * FROM cron.job WHERE jobname = 'password-expiry-notifications-with-logging';

-- Query to view cron job execution logs
-- SELECT * FROM public.cron_job_logs ORDER BY execution_time DESC LIMIT 10;

-- To manually test the cron job, you can run:
-- SELECT cron.schedule('test-password-expiry', '* * * * *', 'SELECT net.http_post(url := ''YOUR_APP_URL/cron/password-expiry-check'', headers := ''{\"Content-Type\": \"application/json\"}''::jsonb);');
-- Then unschedule it after testing:
-- SELECT cron.unschedule('test-password-expiry');