import os
import secrets
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client
from passwordHash import hash_password
from EmailUser import send_email

def _sb() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')
    if not url or not key:
        raise RuntimeError("Supabase environment is not configured")
    return create_client(url, key)

def _now_utc():
    return datetime.now(timezone.utc)

def _password_policy_ok(pw: str):
    if not pw or len(pw) < 8:
        return False, "Password must be at least 8 characters long"
    if not pw[0].isalpha():
        return False, "Password must start with a letter"
    has_letter = any(c.isalpha() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_special = any(not c.isalnum() for c in pw)
    if not (has_letter and has_digit and has_special):
        return False, "Password must include a letter, a number, and a special character"
    return True, "OK"

def _slugify_name(s: str) -> str:
    return ''.join(ch for ch in s.lower() if ch.isalpha())

def _generate_username(first_name: str, last_name: str, created_at: datetime, sb: Client) -> str:
    base = f"{_slugify_name(first_name)[:1]}{_slugify_name(last_name)}{created_at.strftime('%m%y')}"
    candidate = base
    suffix = 1
    while True:
        resp = sb.table('Users').select('Username').eq('Username', candidate).execute()
        if not resp.data:
            return candidate
        suffix += 1
        candidate = f"{base}{suffix}"

def create_signup_invitation(request_id: int, reviewer_user_id: int, expires_in_hours: int = 48):
    sb = _sb()
    # Load request
    req = sb.table('registration_requests').select('*').eq('RequestID', request_id).single().execute()
    if not req.data:
        return {'success': False, 'message': 'Registration request not found'}
    # Mark approved
    sb.table('registration_requests').update({
        'Status': 'Approved',
        'ReviewedByUserID': reviewer_user_id,
        'ReviewDate': 'now()'
    }).eq('RequestID', request_id).execute()
    # Create token
    token = secrets.token_urlsafe(32)
    expires_at = (_now_utc() + timedelta(hours=expires_in_hours)).isoformat()
    sb.table('signup_invitations').insert({
        'RequestID': request_id,
        'Token': token,
        'ExpiresAt': expires_at
    }).execute()
    # Email the link
    base_url = os.environ.get('BASE_URL') or os.environ.get('RENDER_EXTERNAL_URL') or 'http://localhost:8000'
    link = f"{base_url}/FinishSignUp?token={token}"
    applicant_email = req.data['Email']
    applicant_name = f"{req.data.get('FirstName','')} {req.data.get('LastName','')}".strip()
    body = f"""
        <p>Hello {applicant_name},</p>
        <p>Your registration has been approved. Click the link below to complete your FinKen account setup:</p>
        <p><a href="{link}">{link}</a></p>
        <p>This link will expire in {expires_in_hours} hours and can be used once.</p>
    """
    email_res = send_email(
        sender_email='notifications@job-fit-ai.com',
        sender_name='FinKen Admin',
        receiver_email=applicant_email,
        subject_line='Complete your FinKen account setup',
        body=body
    )
    if not email_res.get('success'):
        return {'success': False, 'message': f"Invitation created but email failed: {email_res.get('error')}"}
    return {'success': True, 'message': 'Invitation created and email sent'}

def get_signup_context(token: str):
    sb = _sb()
    inv = sb.table('signup_invitations').select('*').eq('Token', token).single().execute()
    if not inv.data:
        return {'success': False, 'message': 'Invalid signup link'}
    if inv.data.get('UsedAt'):
        return {'success': False, 'message': 'This signup link was already used'}
    if datetime.fromisoformat(inv.data['ExpiresAt']) < _now_utc():
        return {'success': False, 'message': 'This signup link has expired'}
    req = sb.table('Registration_Requests').select('*').eq('RequestID', inv.data['RequestID']).single().execute()
    if not req.data or req.data.get('Status') != 'Approved':
        return {'success': False, 'message': 'Registration is not in an approvable state'}
    qs = sb.table('security_questions').select('QuestionID,QuestionText').order('QuestionText').execute()
    return {
        'success': True,
        'request': req.data,
        'security_questions': qs.data or [],
    }

def finalize_signup(token: str, password: str, confirm_password: str, question_id: int, answer: str):
    sb = _sb()
    # Validate token and request
    ctx = get_signup_context(token)
    if not ctx.get('success'):
        return ctx
    # Validate form
    if not password or not confirm_password or password != confirm_password:
        return {'success': False, 'message': 'Passwords do not match'}
    ok, msg = _password_policy_ok(password)
    if not ok:
        return {'success': False, 'message': msg}
    if not question_id or not answer or not str(answer).strip():
        return {'success': False, 'message': 'Security question and answer are required'}
    req = ctx['request']
    # Build username and hash secrets
    created_at = _now_utc()
    username = _generate_username(req['FirstName'], req['LastName'], created_at, sb)
    pw_hash = hash_password(password)
    answer_hash = hash_password(answer.strip())
    # Insert user
    ins = sb.table('users').insert({
        'Username': username,
        'PasswordHash': pw_hash,
        'FirstName': req['FirstName'],
        'LastName': req['LastName'],
        'Email': req['Email'],
        'DOB': req.get('DOB'),
        'Address': req.get('Address') or '',
        'RoleID': 3,  # default accountant
        'IsActive': True,
        'IsSuspended': False,
        'FailedLoginAttempts': 0,
        'DateCreated': created_at.isoformat()
    }).execute()
    if not ins.data:
        return {'success': False, 'message': 'Could not create user account'}
    user_id = ins.data[0]['UserID']
    # Password history
    sb.table('password_history').insert({
        'UserID': user_id,
        'PasswordHash': pw_hash,
        'DateSet': created_at.isoformat()
    }).execute()
    # Security answer
    sb.table('user_security_answers').insert({
        'UserID': user_id,
        'QuestionID': int(question_id),
        'AnswerHash': answer_hash
    }).execute()
    # Mark invitation used
    sb.table('signup_invitations').update({
        'UsedAt': 'now()'
    }).eq('Token', token).execute()
    return {'success': True, 'message': 'Account created successfully', 'username': username, 'user_id': user_id}