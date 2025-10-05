from AdminManagement import *
from conftest import FakeQuery

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