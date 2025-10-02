import os
import math
from datetime import datetime, timezone
from supabase import create_client, Client
from FinishSignUp import create_signup_invitation
from dotenv import load_dotenv

load_dotenv()

def _sb() -> Client:
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_ANON_KEY')
    if not url or not key:
        raise RuntimeError("Supabase environment is not configured")
    return create_client(url, key)

def get_pending_registration_requests():
    """
    Get all pending registration requests for admin review.
    
    Returns:
        dict: Response with success flag and list of pending requests
    """
    try:
        sb = _sb()
        
        # Get all pending registration requests
        response = sb.table('registration_requests').select('*').eq('Status', 'Pending').order('RequestDate', desc=True).execute()
        
        if response.data:
            return {
                'success': True,
                'requests': response.data
            }
        else:
            return {
                'success': True,
                'requests': []
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving registration requests: {str(e)}',
            'requests': []
        }

def get_all_registration_requests(page=1, per_page=20, search_term='', status_filter=''):
    """
    Get all registration requests (pending, approved, rejected) for admin review with pagination.
    
    Args:
        page (int): Current page number (1-based)
        per_page (int): Number of requests per page
        search_term (str): Search term for name or email
        status_filter (str): Filter by status ('Pending', 'Approved', 'Rejected', or empty for all)
    
    Returns:
        dict: Response with success flag, list of requests, and pagination info
    """
    try:
        sb = _sb()
        
        # Start building the query
        query = sb.table('registration_requests').select('''
            *,
            reviewer:ReviewedByUserID(Username, FirstName, LastName)
        ''')
        
        # Apply search filter if provided
        if search_term:
            query = query.or_(
                f'FirstName.ilike.%{search_term}%,'
                f'LastName.ilike.%{search_term}%,'
                f'Email.ilike.%{search_term}%'
            )
        
        # Apply status filter if provided
        if status_filter:
            query = query.eq('Status', status_filter)
        
        # Get total count for pagination (before applying limit/offset)
        count_query = sb.table('registration_requests').select('RequestID', count='exact')
        
        # Apply same filters to count query
        if search_term:
            count_query = count_query.or_(
                f'FirstName.ilike.%{search_term}%,'
                f'LastName.ilike.%{search_term}%,'
                f'Email.ilike.%{search_term}%'
            )
        
        if status_filter:
            count_query = count_query.eq('Status', status_filter)
        
        # Execute count query
        count_response = count_query.execute()
        total_requests = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        
        # Calculate pagination
        total_pages = math.ceil(total_requests / per_page) if total_requests > 0 else 1
        offset = (page - 1) * per_page
        
        # Apply pagination and ordering
        query = query.order('RequestDate', desc=True).range(offset, offset + per_page - 1)
        
        # Execute the main query
        response = query.execute()
        
        # Pagination info
        pagination = {
            'current_page': page,
            'per_page': per_page,
            'total_requests': total_requests,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        if response.data:
            return {
                'success': True,
                'requests': response.data,
                'pagination': pagination
            }
        else:
            return {
                'success': True,
                'requests': [],
                'pagination': pagination
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving registration requests: {str(e)}',
            'requests': [],
            'pagination': {'current_page': 1, 'total_pages': 1, 'total_requests': 0}
        }

def approve_registration_request(request_id: int, reviewer_user_id: int, expires_in_hours: int = 48):
    """
    Approve a registration request and send signup invitation email.
    
    Args:
        request_id (int): The RequestID to approve
        reviewer_user_id (int): The UserID of the administrator approving the request
        expires_in_hours (int): Hours until the signup link expires (default 48)
        
    Returns:
        dict: Response with success flag and message
    """
    try:
        sb = _sb()
        
        # Check if request exists and is pending
        req_response = sb.table('registration_requests').select('*').eq('RequestID', request_id).single().execute()
        
        if not req_response.data:
            return {
                'success': False,
                'message': 'Registration request not found'
            }
        
        request_data = req_response.data
        
        if request_data.get('Status') != 'Pending':
            return {
                'success': False,
                'message': f'Registration request is already {request_data.get("Status", "processed")}'
            }
        
        # Use the existing function from FinishSignUp.py to create invitation and send email
        result = create_signup_invitation(request_id, reviewer_user_id, expires_in_hours)
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error approving registration request: {str(e)}'
        }

def reject_registration_request(request_id: int, reviewer_user_id: int, rejection_reason: str = None):
    """
    Reject a registration request.
    
    Args:
        request_id (int): The RequestID to reject
        reviewer_user_id (int): The UserID of the administrator rejecting the request
        rejection_reason (str): Optional reason for rejection
        
    Returns:
        dict: Response with success flag and message
    """
    try:
        sb = _sb()
        
        # Check if request exists and is pending
        req_response = sb.table('registration_requests').select('*').eq('RequestID', request_id).single().execute()
        
        if not req_response.data:
            return {
                'success': False,
                'message': 'Registration request not found'
            }
        
        request_data = req_response.data
        
        if request_data.get('Status') != 'Pending':
            return {
                'success': False,
                'message': f'Registration request is already {request_data.get("Status", "processed")}'
            }
        
        # Update the request status to rejected
        update_data = {
            'Status': 'Rejected',
            'ReviewedByUserID': reviewer_user_id,
            'ReviewDate': datetime.now(timezone.utc).isoformat()
        }
        
        # Add rejection reason if provided (you may need to add this column to your schema)
        if rejection_reason:
            update_data['RejectionReason'] = rejection_reason
        
        response = sb.table('registration_requests').update(update_data).eq('RequestID', request_id).execute()
        
        if response.data:
            return {
                'success': True,
                'message': 'Registration request rejected successfully'
            }
        else:
            return {
                'success': False,
                'message': 'Failed to update registration request status'
            }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error rejecting registration request: {str(e)}'
        }

def get_registration_request_details(request_id: int):
    """
    Get detailed information about a specific registration request.
    
    Args:
        request_id (int): The RequestID to get details for
        
    Returns:
        dict: Response with success flag and request details
    """
    try:
        sb = _sb()
        
        # Get the registration request with reviewer information
        response = sb.table('registration_requests').select('''
            *,
            reviewer:ReviewedByUserID(Username, FirstName, LastName)
        ''').eq('RequestID', request_id).single().execute()
        
        if response.data:
            return {
                'success': True,
                'request': response.data
            }
        else:
            return {
                'success': False,
                'message': 'Registration request not found'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error retrieving registration request details: {str(e)}'
        }