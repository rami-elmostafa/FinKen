# UserManagement.py

import os
import math
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_users_paginated(page=1, per_page=10, search_term='', status_filter=''):
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
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'message': 'Database configuration error - Supabase credentials not found'
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Start building the query
        query = supabase.table('users').select(
            'UserID, Username, FirstName, LastName, Email, DOB, Address, '
            'IsActive, IsSuspended, DateCreated, ProfilePictureURL, '
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
        count_query = supabase.table('users').select('UserID', count='exact')
        
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
                    'ProfilePictureURL': user.get('ProfilePictureURL')
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

def update_user_status(user_id, action):
    """
    Update user status (activate, deactivate, suspend, unsuspend)
    
    Args:
        user_id (int): The user ID to update
        action (str): Action to perform ('activate', 'deactivate', 'suspend', 'unsuspend')
    
    Returns:
        dict: Success status and message
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'message': 'Database configuration error - Supabase credentials not found'
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Determine the update values based on action
        update_data = {}
        
        if action == 'activate':
            update_data = {'IsActive': True, 'IsSuspended': False}
        elif action == 'deactivate':
            update_data = {'IsActive': False, 'IsSuspended': False}
        elif action == 'suspend':
            update_data = {'IsSuspended': True}
        elif action == 'unsuspend':
            update_data = {'IsSuspended': False}
        else:
            return {
                'success': False,
                'message': f'Invalid action: {action}'
            }
        
        # Update the user
        response = supabase.table('users').update(update_data).eq('UserID', user_id).execute()
        
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

def get_user_by_id(user_id):
    """
    Get a specific user by ID
    
    Args:
        user_id (int): The user ID to fetch
    
    Returns:
        dict: User data and success status
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'message': 'Database configuration error - Supabase credentials not found'
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Get the user
        response = supabase.table('users').select(
            'UserID, Username, FirstName, LastName, Email, DOB, Address, '
            'IsActive, IsSuspended, DateCreated, roles(RoleName)'
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
                'Status': status,
                'RoleName': user.get('roles', {}).get('RoleName') if user.get('roles') else 'Unknown',
                'DateCreated': user.get('DateCreated')
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

def get_expiring_passwords(days_ahead=30):
    """
    Get users whose passwords will expire within the specified number of days
    
    Args:
        days_ahead (int): Number of days to look ahead for expiring passwords
    
    Returns:
        dict: Contains users with expiring passwords and success status
    """
    try:
        # Initialize Supabase client
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_key = os.environ.get('SUPABASE_ANON_KEY')
        
        if not supabase_url or not supabase_key:
            return {
                'success': False,
                'message': 'Database configuration error - Supabase credentials not found'
            }
        
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() + timedelta(days=days_ahead)
        cutoff_date_str = cutoff_date.isoformat()
        
        # Get users whose passwords expire within the specified timeframe
        response = supabase.table('users').select(
            'UserID, Username, FirstName, LastName, Email, PasswordExpiryDate, '
            'IsActive, roles(RoleName)'
        ).lte('PasswordExpiryDate', cutoff_date_str).eq('IsActive', True).order('PasswordExpiryDate').execute()
        
        if not response.data:
            users = []
        else:
            users = []
            for user in response.data:
                # Only include users that actually have a password expiry date
                if user.get('PasswordExpiryDate'):
                    expiry_date = datetime.fromisoformat(user['PasswordExpiryDate'].replace('Z', '+00:00'))
                    days_until_expiry = (expiry_date - datetime.now()).days
                    
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
                        'IsExpiringSoon': 0 <= days_until_expiry <= 7
                    }
                    users.append(user_data)
        
        return {
            'success': True,
            'users': users,
            'total_count': len(users)
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching expiring passwords: {str(e)}'
        }