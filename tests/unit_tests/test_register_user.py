import pytest
from server.handlers.auth import register_user
from server.models.user import UserRole

def test_register_user_success():
    users = {}

    user, error = register_user(users, "alice")
    assert error is None
    assert user is not None
    assert user.username == "alice"
    assert user.user_role == UserRole.USER
    assert user.user_id in users

def test_register_user_duplicate():
    users = {}

    user, error = register_user(users, "alice")
    assert error is None
    assert user is not None
    assert user.username == "alice"
    assert user.user_role == UserRole.USER
    assert user.user_id in users

    user, error = register_user(users, "alice")
    assert error == "duplicate"
    assert user is None
    assert len(users) == 1

def test_register_user_admin_flag():
    users = {}

    user, error = register_user(users, "alice", is_admin=True)

    assert error is None
    assert user.user_role == UserRole.ADMIN
    assert len(users) == 1

