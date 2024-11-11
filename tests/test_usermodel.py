import pytest
from config import db, app  # Import the app instance
from models import User  # Adjust the import path based on your project structure

@pytest.fixture
def new_user():
    user = User(name="Liza", email="liza@example.com", role="customer")
    user.set_password("securepassword123")
    return user

@pytest.fixture(scope="module")
def test_db():
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

def test_set_password(new_user):
    assert new_user.password_hash is not None

def test_check_password(new_user):
    assert new_user.check_password("securepassword123") is True
    assert new_user.check_password("wrongpassword") is False

def test_is_admin(new_user):
    assert new_user.is_admin() is False
    new_user.role = "admin"
    assert new_user.is_admin() is True

def test_is_valid_email():
    assert User.is_valid_email("valid@example.com") is True
    assert User.is_valid_email("invalid-email.com") is False

def test_role_constraint(test_db):
    with app.app_context():
        # Valid role should work
        user = User(name="AdminUser", email="admin@example.com", role="admin")
        user.set_password("securepassword123")  # Set a password
        db.session.add(user)
        db.session.commit()

        # Invalid role should raise an IntegrityError
        with pytest.raises(Exception):
            invalid_user = User(name="InvalidUser", email="invalid@example.com", role="guest")
            invalid_user.set_password("password123")  # Set a password for consistency
            db.session.add(invalid_user)
            db.session.commit()

def test_unique_email_constraint(test_db):
    with app.app_context():
        user1 = User(name="User1", email="unique@example.com", role="customer")
        user1.set_password("password1")
        db.session.add(user1)
        db.session.commit()

        # Attempt to add another user with the same email should raise an IntegrityError
        user2 = User(name="User2", email="unique@example.com", role="customer")
        user2.set_password("password2")
        with pytest.raises(Exception):
            db.session.add(user2)
            db.session.commit()
