# UserManagement.py

import math
from datetime import datetime, timedelta, timezone
from SupabaseClient import _sb

def get_users_paginated(page=1, per_page=10, search_term='', status_filter='', sb = None):
    """
    Get users with pagination and filtering
    
    Args:
        page (int): Current page number (1-based)
        per_page (int): Number of users per page
        search_term (str): Search term for name or email
        status_filter (str): Filter by user status ('active', 'inactive', 'suspended', or empty for all)
    
    Returns:
        dict: Contains users data, pagination info, and success status
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Start building the query
        query = sb.table('users').select(
            'UserID, Username, FirstName, LastName, Email, DOB, Address, '
            'IsActive, IsSuspended, SuspensionEndDate, SuspensionReason, '
            'DateCreated, ProfilePictureURL, '
            'roles(RoleName)'
        )
        
        # Apply search filter if provided
        if search_term:
            # Convert search term to lowercase for case-insensitive search
            search_lower = search_term.lower()
            # Use or_ to search across multiple fields
            query = query.or_(
                f'FirstName.ilike.%{search_term}%,'
                f'LastName.ilike.%{search_term}%,'
                f'Email.ilike.%{search_term}%,'
                f'Username.ilike.%{search_term}%'
            )
        
        # Apply status filter if provided
        if status_filter == 'active':
            query = query.eq('IsActive', True).eq('IsSuspended', False)
        elif status_filter == 'inactive':
            query = query.eq('IsActive', False)
        elif status_filter == 'suspended':
            query = query.eq('IsSuspended', True)
        
        # Get total count for pagination (before applying limit/offset)
        count_query = sb.table('users').select('UserID', count='exact')
        
        # Apply same filters to count query
        if search_term:
            count_query = count_query.or_(
                f'FirstName.ilike.%{search_term}%,'
                f'LastName.ilike.%{search_term}%,'
                f'Email.ilike.%{search_term}%,'
                f'Username.ilike.%{search_term}%'
            )
        
        if status_filter == 'active':
            count_query = count_query.eq('IsActive', True).eq('IsSuspended', False)
        elif status_filter == 'inactive':
            count_query = count_query.eq('IsActive', False)
        elif status_filter == 'suspended':
            count_query = count_query.eq('IsSuspended', True)
        
        # Execute count query
        count_response = count_query.execute()
        total_users = count_response.count if hasattr(count_response, 'count') else len(count_response.data)
        
        # Calculate pagination
        total_pages = math.ceil(total_users / per_page) if total_users > 0 else 1
        offset = (page - 1) * per_page
        
        # Apply pagination and ordering
        query = query.order('DateCreated', desc=True).range(offset, offset + per_page - 1)
        
        # Execute the main query
        response = query.execute()
        
        if not response.data:
            users = []
        else:
            users = []
            for user in response.data:
                # Determine user status
                if user.get('IsSuspended'):
                    status = 'suspended'
                elif user.get('IsActive'):
                    status = 'active'
                else:
                    status = 'inactive'
                
                # Format the user data
                user_data = {
                    'UserID': user.get('UserID'),
                    'Username': user.get('Username'),
                    'FirstName': user.get('FirstName'),
                    'LastName': user.get('LastName'),
                    'Email': user.get('Email'),
                    'DOB': user.get('DOB'),
                    'Address': user.get('Address'),
                    'Status': status,
                    'RoleName': user.get('roles', {}).get('RoleName') if user.get('roles') else 'Unknown',
                    'DateCreated': user.get('DateCreated'),
                    'ProfilePictureURL': user.get('ProfilePictureURL'),
                    'SuspensionEndDate': user.get('SuspensionEndDate'),
                    'SuspensionReason': user.get('SuspensionReason')
                }
                users.append(user_data)
        
        # Pagination info
        pagination = {
            'current_page': page,
            'per_page': per_page,
            'total_users': total_users,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None
        }
        
        return {
            'success': True,
            'users': users,
            'pagination': pagination
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching users: {str(e)}'
        }

def update_user_status(user_id, action, sb = None, suspension_data=None):
    """
    Update user status (activate, deactivate, suspend, unsuspend)
    
    Args:
        user_id (int): The user ID to update
        action (str): Action to perform ('activate', 'deactivate', 'suspend', 'unsuspend')
        suspension_data (dict): Optional suspension details for suspend action
    
    Returns:
        dict: Success status and message
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Determine the update values based on action
        update_data = {}
        
        if action == 'activate':
            update_data = {
                'IsActive': True, 
                'IsSuspended': False,
                'SuspensionEndDate': None,
                'SuspensionReason': None
            }
        elif action == 'deactivate':
            update_data = {
                'IsActive': False, 
                'IsSuspended': False,
                'SuspensionEndDate': None,
                'SuspensionReason': None
            }
        elif action == 'suspend':
            if not suspension_data or not suspension_data.get('end_date'):
                return {
                    'success': False,
                    'message': 'Suspension end date is required'
                }
            
            update_data = {
                'IsSuspended': True,
                'SuspensionEndDate': suspension_data['end_date'],
                'SuspensionReason': suspension_data.get('reason', 'No reason provided')
            }
        elif action == 'unsuspend':
            update_data = {
                'IsSuspended': False,
                'SuspensionEndDate': None,
                'SuspensionReason': None
            }
        else:
            return {
                'success': False,
                'message': f'Invalid action: {action}'
            }
        
        # Update the user
        response = sb.table('users').update(update_data).eq('UserID', user_id).execute()
        
        if response.data:
            return {
                'success': True,
                'message': f'User {action}d successfully'
            }
        else:
            return {
                'success': False,
                'message': 'User not found or update failed'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error updating user status: {str(e)}'
        }

def get_user_by_id(user_id, sb = None):
    """
    Get a specific user by ID
    
    Args:
        user_id (int): The user ID to fetch
    
    Returns:
        dict: User data and success status
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Get the user
        response = sb.table('users').select(
            'UserID, Username, FirstName, LastName, Email, DOB, Address, RoleID, '
            'IsActive, IsSuspended, SuspensionEndDate, SuspensionReason, '
            'DateCreated, roles(RoleID, RoleName)'
        ).eq('UserID', user_id).execute()
        
        if response.data and len(response.data) > 0:
            user = response.data[0]
            
            # Determine user status
            if user.get('IsSuspended'):
                status = 'suspended'
            elif user.get('IsActive'):
                status = 'active'
            else:
                status = 'inactive'
            
            user_data = {
                'UserID': user.get('UserID'),
                'Username': user.get('Username'),
                'FirstName': user.get('FirstName'),
                'LastName': user.get('LastName'),
                'Email': user.get('Email'),
                'DOB': user.get('DOB'),
                'Address': user.get('Address'),
                'RoleID': user.get('RoleID'),
                'Status': status,
                'RoleName': user.get('roles', {}).get('RoleName') if user.get('roles') else 'Unknown',
                'DateCreated': user.get('DateCreated'),
                'SuspensionEndDate': user.get('SuspensionEndDate'),
                'SuspensionReason': user.get('SuspensionReason')
            }
            
            return {
                'success': True,
                'user': user_data
            }
        else:
            return {
                'success': False,
                'message': 'User not found'
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching user: {str(e)}'
        }

def get_expiring_passwords(days_ahead=30, show_all=False, sb = None):
    """
    Get users whose passwords will expire within the specified number of days
    
    Args:
        days_ahead (int): Number of days to look ahead for expiring passwords
        show_all (bool): If True, show all users regardless of expiry date
    
    Returns:
        dict: Contains users with password expiry information and success status
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        if show_all:
            # Get all active users
            response = sb.table('users').select(
                'UserID, Username, FirstName, LastName, Email, PasswordExpiryDate, '
                'IsActive, roles(RoleName)'
            ).eq('IsActive', True).order('PasswordExpiryDate', desc=False).execute()
        else:
            # Calculate the cutoff date
            cutoff_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
            cutoff_date_str = cutoff_date.isoformat()
            
            # Get users whose passwords expire within the specified timeframe
            response = sb.table('users').select(
                'UserID, Username, FirstName, LastName, Email, PasswordExpiryDate, '
                'IsActive, roles(RoleName)'
            ).lte('PasswordExpiryDate', cutoff_date_str).eq('IsActive', True).order('PasswordExpiryDate').execute()
        
        if not response.data:
            users = []
        else:
            users = []
            for user in response.data:
                # Calculate days until expiry if user has an expiry date
                if user.get('PasswordExpiryDate'):
                    expiry_date = datetime.fromisoformat(user['PasswordExpiryDate'].replace('Z', '+00:00'))
                    # Make datetime.now() timezone-aware to match the expiry_date
                    now = datetime.now(timezone.utc)
                    days_until_expiry = (expiry_date - now).days
                    
                    user_data = {
                        'UserID': user.get('UserID'),
                        'Username': user.get('Username'),
                        'FirstName': user.get('FirstName'),
                        'LastName': user.get('LastName'),
                        'Email': user.get('Email'),
                        'PasswordExpiryDate': user.get('PasswordExpiryDate'),
                        'DaysUntilExpiry': days_until_expiry,
                        'RoleName': user.get('roles', {}).get('RoleName') if user.get('roles') else 'Unknown',
                        'IsExpired': days_until_expiry < 0,
                        'IsExpiringSoon': 0 <= days_until_expiry <= 7,
                        'HasExpiryDate': True
                    }
                else:
                    # User has no expiry date
                    user_data = {
                        'UserID': user.get('UserID'),
                        'Username': user.get('Username'),
                        'FirstName': user.get('FirstName'),
                        'LastName': user.get('LastName'),
                        'Email': user.get('Email'),
                        'PasswordExpiryDate': None,
                        'DaysUntilExpiry': None,
                        'RoleName': user.get('roles', {}).get('RoleName') if user.get('roles') else 'Unknown',
                        'IsExpired': False,
                        'IsExpiringSoon': False,
                        'HasExpiryDate': False
                    }
                
                users.append(user_data)
        
        # Count users with expiring passwords
        expiring_count = sum(1 for user in users if user.get('HasExpiryDate') and 
                           user.get('DaysUntilExpiry') is not None and 
                           user.get('DaysUntilExpiry') <= days_ahead)
        
        return {
            'success': True,
            'users': users,
            'total_count': len(users),
            'expiring_count': expiring_count,
            'show_all': show_all,
            'days_ahead': days_ahead
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching password expiry data: {str(e)}'
        }

def get_all_roles(sb = None):
    """
    Get all available roles from the database
    
    Returns:
        dict: Contains roles data and success status
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Get all roles
        response = sb.table('roles').select('RoleID, RoleName').order('RoleName').execute()
        
        if response.data:
            return {
                'success': True,
                'roles': response.data
            }
        else:
            return {
                'success': True,
                'roles': []
            }
            
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching roles: {str(e)}'
        }

def check_and_unsuspend_users(sb = None):
    """
    Check for users whose suspension period has ended and automatically unsuspend them
    
    Returns:
        dict: Contains count of users unsuspended and success status
    """
    try:
        # Initialize Supabase client
        sb = sb or _sb()
        
        # Get current timestamp
        current_time = datetime.now(timezone.utc).isoformat()
        
        # Find users who are suspended but their suspension end date has passed
        response = sb.table('users').select(
            'UserID, FirstName, LastName, SuspensionEndDate'
        ).eq('IsSuspended', True).lte('SuspensionEndDate', current_time).execute()
        
        unsuspended_count = 0
        unsuspended_users = []
        
        if response.data:
            for user in response.data:
                # Unsuspend the user
                update_result = update_user_status(user['UserID'], 'unsuspend', sb, None)
                if update_result['success']:
                    unsuspended_count += 1
                    unsuspended_users.append({
                        'UserID': user['UserID'],
                        'Name': f"{user['FirstName']} {user['LastName']}",
                        'SuspensionEndDate': user['SuspensionEndDate']
                    })
        
        return {
            'success': True,
            'unsuspended_count': unsuspended_count,
            'unsuspended_users': unsuspended_users,
            'message': f'Automatically unsuspended {unsuspended_count} users'
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error checking suspensions: {str(e)}'
        }