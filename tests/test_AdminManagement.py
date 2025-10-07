from AdminManagement import *
from conftest import FakeQuery
#Get Pending Registration Requests Tests
def test_get_pending_requests_none(fake_sb_factory):
    sb = fake_sb_factory({
        ('registration_requests', 'select'): []
    })
    out = get_pending_registration_requests(sb = sb)
    assert out == {
        'success': True,
        'message': 'No pending registration requests found',
        'data': []
    }

def test_get_pending_requests_success(fake_sb_factory):
    sb = fake_sb_factory({
        ('registration_requests', 'select'): [
            {'RequestID': 1, 'FirstName': 'John', 'LastName': 'Doe', 'Email': 'johndoe@gmail.com', 'DOB': '1990-01-01', 'Address': '123 Main St', 'RequestDate': '2023-01-01T00:00:00', 'Status': 'Pending'},
            {'RequestID': 2, 'FirstName': 'Jane', 'LastName': 'Doe', 'Email': 'janedoe@gmail.com', 'DOB': '1992-02-02', 'Address': '456 Elm St', 'RequestDate': '2023-02-01T00:00:00', 'Status': 'Pending'}
        ]
    })
    out = get_pending_registration_requests(sb = sb)
    assert out == {
        'success': True,
        'requests': { 
            {'RequestID': 1, 'FirstName': 'John', 'LastName': 'Doe', 'Email': 'johndoe@gmail.com', 'DOB': '1990-01-01', 'Address': '123 Main St', 'RequestDate': '2023-01-01T00:00:00', 'Status': 'Pending'},
            {'RequestID': 2, 'FirstName': 'Jane', 'LastName': 'Doe', 'Email': 'janedoe@gmail.com', 'DOB': '1992-02-02', 'Address': '456 Elm St', 'RequestDate': '2023-02-01T00:00:00', 'Status': 'Pending'}}
    }

#Get All Registration Requests Tests
def test_get_all_requests_none(fake_sb_factory):
    sb = fake_sb_factory({
        ('registration_requests', 'select'): []
    })
    out = get_all_registration_requests(sb = sb)
    assert out == {
        'success': True,
        'message': 'No registration requests found',
        'data': []
    }


#Suspend User Tests
def test_suspend_invalid_date_format(fake_sb_factory):
    sb = fake_sb_factory({})
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "invalid-date", sb = sb)
    assert out == {
        'success': False,
        'message': 'Invalid date format. Use YYYY-MM-DD.'}

def test_suspend_empty(fake_sb_factory):
    sb = fake_sb_factory({})
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = None, sb = sb)
    assert out == {
        'success': False,
        'message': 'Suspension end date is required'}

def test_suspend_past_date(fake_sb_factory):
    sb = fake_sb_factory({})
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2001-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'Suspension end date must be in the future'}
    
def test_suspend_admin_not_found(fake_sb_factory):
    sb = fake_sb_factory(
        { ('users', 'select'): None })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'Admin user not found'}
    
def test_suspend_admin_only_permissions(fake_sb_factory):
    sb = fake_sb_factory(
        { ('users', 'select'): {'UserID': 1, 'RoleID': 2} })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'Only administrators can suspend user accounts'}

def test_suspend_user_not_found(fake_sb_factory):
    sb = fake_sb_factory({
        ('users', 'select'): [ 
            {'UserID': 1, 'RoleID': 1}, 
            None
        ] 
    })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'User not found'}
    
def test_suspend_user_inactive(fake_sb_factory):
    sb = fake_sb_factory({
        ('users', 'select'): [
            {'UserID': 1, 'RoleID': 1},
            {'UserID': 2, 'IsActive': False}
        ]
    })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'User account has not been activated'}
    
def test_suspend_user_already_suspended(fake_sb_factory):
    sb = fake_sb_factory({
        ('users', 'select'): [
            {'UserID': 1, 'RoleID': 1},
            {'UserID': 2, 'IsActive': True, 'IsSuspended': True}
        ]
    })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': False,
        'message': 'User account is already suspended'}

def test_suspend_success(fake_sb_factory):
    sb = fake_sb_factory({
        ('users', 'select'): [
            {'UserID': 1, 'RoleID': 1},
            {'UserID': 2, 'IsActive': True, 'IsSuspended': False} 
        ],
        ('users', 'update'): {'UserID': 2, 'IsSuspended': True, 'SuspensionEndDate': '2030-01-01'}
    })
    out = suspend_user_account(user_id = 1, admin_user_id = 1, suspension_end_date = "2030-01-01", sb = sb)
    assert out == {
        'success': True,
        'message': 'User account suspended successfully'}
    

#sanity check can delete later if so choose
from ForgotPassword import find_user

def test_findUser(fake_sb_factory):
    sb = fake_sb_factory({
        ('users', 'select'): [{'UserID': 1, 'Email': 'crb@gmail.com'}]
    })
    out = find_user(userid = 1, email = 'crb@gmail.com', sb = sb)
    assert out == {
        'success': True,
        'message': 'User exists'
    }
