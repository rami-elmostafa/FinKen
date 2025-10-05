import math
from datetime import datetime, timezone
from FinishSignUp import create_signup_invitation
from SupabaseClient import _sb

def get_pending_registration_requests(sb = None):
    """
    Get all pending registration requests for admin review.
    
    Returns:
        dict: Response with success flag and list of pending requests
    """
    try:
        sb = sb or _sb()
        
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

def get_all_registration_requests(page=1, per_page=20, search_term='', status_filter='', sb = None):
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
        sb = sb or _sb()
        
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

def approve_registration_request(request_id: int, reviewer_user_id: int, expires_in_hours: int = 48, sb = None):
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
        sb = sb or _sb()
        
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

def reject_registration_request(request_id: int, reviewer_user_id: int, rejection_reason: str = None, sb = None):
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
        sb = sb or _sb()
        
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

def get_registration_request_details(request_id: int, sb = None):
    """
    Get detailed information about a specific registration request.
    
    Args:
        request_id (int): The RequestID to get details for
        
    Returns:
        dict: Response with success flag and request details
    """
    try:
        sb = sb or _sb()
        
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
    
def suspend_user_account(user_id: int, admin_user_id: int, suspension_end_date: datetime.date, reason: str = None, sb = None):
    """
    Suspend a user account.
    
    Args:
        user_id (int): The UserID of the account to suspend
        admin_user_id (int): The UserID of the administrator performing the suspension

        reason (str): Optional reason for suspension
        
    Returns:
        dict: Response with success flag and message
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Validate suspension_end_date format
        if not suspension_end_date:
            return {
                'success': False,
                'message': 'Suspension end date is required'
            }
        
        try:
            suspension_end_date = datetime.strptime(suspension_end_date, '%Y-%m-%d')
        except ValueError:
            return {
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD.'
            }
            
        if suspension_end_date < datetime.now():
            return {
                'success': False,
                'message': 'Suspension end date must be in the future'
            }

        # Check if admin user exists and is an administrator
        response = sb.table('users').select('*').eq('UserID', admin_user_id).single().execute()

        if not response.data:
            return {
                'success': False,
                'message': 'Admin user not found'
            }
        
        if not response.data.get('RoleID') == 1:
            return {
                'success': False,
                'message': 'Only administrators can suspend user accounts'
            }

        
        # Check if user exists
        user_response = sb.table('users').select('*').eq('UserID', user_id).single().execute()
        if not user_response.data:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Check if the user has been activated
        user_data = user_response.data
        if not user_data.get('IsActive', False):
            return {
                'success': False,
                'message': 'User account has not been activated'
            }
        
        # Check if user is already suspended
        if user_data.get('IsSuspended', False):
            return {
                'success': False,
                'message': 'User account is already suspended'
            }
        
        # Update the user's IsSuspended status
        update_data = {
            'IsSuspended': True,
            'LastModifiedBy': admin_user_id,
            'LastModifiedDate': datetime.now(timezone.utc).isoformat()
        }
        
        # Log reason for suspension (optional)
        if reason:
            update_data['SuspensionReason'] = reason
        
        # Check if update was successful
        response = sb.table('users').update(update_data).eq('UserID', user_id).execute()
        if not response.data:
            return {
                'success': False,
                'message': 'Failed to suspend user account'
            }
        
        return {
            'success': True,
            'message': 'User account suspended successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error suspending user account: {str(e)}'
        }
    
def unsuspend_user_account(user_id: int, admin_user_id: int = None, sb = None):
    """
    Unsuspend a user account.
    
    Args:
        user_id (int): The UserID of the account to unsuspend
        admin_user_id (int): The UserID of the administrator performing the unsuspension (Optional)
        
    Returns:
        dict: Response with success flag and message
    """
    try:
        sb = sb or _sb()
        
        # Check if user exists and is suspended
        user_response = sb.table('users').select('*').eq('UserID', user_id).single().execute()
        
        if not user_response.data:
            return {
                'success': False,
                'message': 'User not found'
            }
        
        # Check if admin user exists and is an administrator
        if admin_user_id:
            response = sb.table('users').select('*').eq('UserID', admin_user_id).single().execute()
            if not response.data or response.data.get('RoleID') != 1:
                return {
                    'success': False,
                    'message': 'Only administrators can unsuspend user accounts'
                }
        elif not user_response.data.get('SuspensionEndDate') == datetime.now():
            return {
                'success': False,
                'message': 'Only administrators can unsuspend user accounts before the suspension end date'
            }
        
        # Check if the user is already suspended
        user_data = user_response.data
        if user_data.get('IsActive', True):
            return {
                'success': False,
                'message': 'User account is not suspended'
            }
        
        # Update the user's IsSuspended status
        update_data = {
            'IsSuspended': False,
            'SuspensionReason': None,
            'SuspensionEndDate': None,
            'LastModifiedBy': admin_user_id,
            'LastModifiedDate': datetime.now(timezone.utc).isoformat()
        }
        response = sb.table('users').update(update_data).eq('UserID', user_id).execute()

        # Check if update was successful
        if  not response.data:
            return {
                'success': False,
                'message': 'Failed to unsuspend user account'
            }
        
        return {
            'success': True,
            'message': 'User account unsuspended successfully'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error unsuspending user account: {str(e)}'
        }
    