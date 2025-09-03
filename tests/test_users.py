import sys
import os
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.storage import usersDB, paymentsDB
from app.models import User, Payment

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test"""
    usersDB.clear()
    paymentsDB.clear()
    yield

class TestGetUsers:
    def test_get_all_users_empty(self):
        """Test getting all users when database is empty"""
        response = client.get("/users/getAll")
        assert response.status_code == 200
        assert response.json() == {"users": []}

    def test_get_all_users_with_data(self):
        """Test getting all users when database has data"""
        test_user1 = User(
            username="testuser1",
            password="hashedpass123",
            email="test1@example.com",
            birthdate="1990-01-01"
        )
        test_user2 = User(
            username="testuser2",
            password="hashedpass456",
            email="test2@example.com",
            birthdate="1995-01-01",
            ccNumber="1234567890123456"
        )
        usersDB.extend([test_user1, test_user2])
        
        response = client.get("/users/getAll")
        assert response.status_code == 200
        users = response.json()["users"]
        assert len(users) == 2
        assert users[0]["username"] == "testuser1"
        assert users[1]["username"] == "testuser2"

    def test_get_users_filter_creditcard_yes(self):
        """Test filtering users with credit cards"""
        test_user1 = User(
            username="testuser1",
            password="hashedpass123",
            email="test1@example.com",
            birthdate="1990-01-01"
        )
        test_user2 = User(
            username="testuser2",
            password="hashedpass456",
            email="test2@example.com",
            birthdate="1995-01-01",
            ccNumber="1234567890123456"
        )
        usersDB.extend([test_user1, test_user2])
        
        response = client.get("/users/getAll?creditcard=yes")
        assert response.status_code == 200
        users = response.json()["users"]
        assert len(users) == 1
        assert users[0]["username"] == "testuser2"

    def test_get_users_filter_creditcard_no(self):
        """Test filtering users without credit cards"""
        test_user1 = User(
            username="testuser1",
            password="hashedpass123",
            email="test1@example.com",
            birthdate="1990-01-01"
        )
        test_user2 = User(
            username="testuser2",
            password="hashedpass456",
            email="test2@example.com",
            birthdate="1995-01-01",
            ccNumber="1234567890123456"
        )
        usersDB.extend([test_user1, test_user2])
        
        response = client.get("/users/getAll?creditcard=no")
        assert response.status_code == 200
        users = response.json()["users"]
        assert len(users) == 1
        assert users[0]["username"] == "testuser1"

    def test_get_users_filter_creditcard_invalid(self):
        """Test filtering with invalid credit card parameter"""
        response = client.get("/users/getAll?creditcard=invalid")
        assert response.status_code == 400
        assert response.json()["message"] == "Invalid creditcard filter. Use 'yes' or 'no'"

class TestGetUserByUsername:
    def test_get_user_by_username_exists(self):
        """Test getting a user that exists"""
        test_user = User(
            username="testuser",
            password="hashedpass123",
            email="test@example.com",
            birthdate="1990-01-01"
        )
        usersDB.append(test_user)
        
        response = client.get("/users/getByUsername/testuser")
        assert response.status_code == 200
        assert response.json()["user"]["username"] == "testuser"

    def test_get_user_by_username_not_exists(self):
        """Test getting a user that doesn't exist"""
        response = client.get("/users/getByUsername/nonexistent")
        assert response.status_code == 404
        assert response.json()["message"] == "User not found"

class TestCreateUser:
    def test_create_user_success(self):
        """Test creating a user with valid data"""
        user_data = {
            "username": "newuser",
            "password": "MyPassword123",
            "email": "newuser@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 201
        assert response.json()["message"] == "User created successfully"
        
        assert len(usersDB) == 1
        assert usersDB[0].username == "newuser"
        assert usersDB[0].email == "newuser@example.com"

    # def test_create_user_with_credit_card(self):
    #     """Test creating a user with valid credit card"""
    #     user_data = {
    #         "username": "carduser",
    #         "password": "MyPassword123",
    #         "email": "carduser@example.com",
    #         "birthdate": "1990-01-01",
    #         "ccNumber": "1234567890123456"
    #     }
        
    #     response = client.post("/users/users/create", json=user_data)
    #     assert response.status_code == 201
    #     assert response.json()["message"] == "User created successfully"
        
    #     assert len(usersDB) == 1
    #     assert len(cardsDB) == 1
    #     assert "1234567890123456" in cardsDB

    def test_create_user_username_not_alphanumeric(self):
        """Test creating user with non-alphanumeric username"""
        user_data = {
            "username": "user-name",
            "password": "MyPassword123",
            "email": "user@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Username must be alphanumeric"

    def test_create_user_username_already_exists(self):
        """Test creating user with existing username"""
        existing_user = User(
            username="existinguser",
            password="hashedpass123",
            email="existing@example.com",
            birthdate="1990-01-01"
        )
        usersDB.append(existing_user)
        
        user_data = {
            "username": "existinguser",
            "password": "MyPassword123",
            "email": "new@example.com",
            "birthdate": "1995-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 409
        assert response.json()["message"] == "Username already exists"

    def test_create_user_password_too_short(self):
        """Test creating user with password less than 8 characters"""
        user_data = {
            "username": "shortpass",
            "password": "Short1",
            "email": "short@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Password must be at least 8 characters long"

    def test_create_user_password_no_uppercase(self):
        """Test creating user with password missing uppercase letter"""
        user_data = {
            "username": "nouppercase",
            "password": "mypassword123",
            "email": "nouppercase@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Password must include at least 1 uppercase letter and 1 number"

    def test_create_user_password_no_number(self):
        """Test creating user with password missing number"""
        user_data = {
            "username": "nonumber",
            "password": "MyPassword",
            "email": "nonumber@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Password must include at least 1 uppercase letter and 1 number"

    def test_create_user_invalid_email(self):
        """Test creating user with invalid email format"""
        user_data = {
            "username": "invalidemail",
            "password": "MyPassword123",
            "email": "invalid-email",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Invalid email format"

    def test_create_user_invalid_date_format(self):
        """Test creating user with invalid date format"""
        user_data = {
            "username": "invaliddate",
            "password": "MyPassword123",
            "email": "date@example.com",
            "birthdate": "01-01-1990"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Birthdate must be in YYYY-MM-DD format"

    def test_create_user_underage(self):
        """Test creating user under 18 years old"""
        user_data = {
            "username": "underage",
            "password": "MyPassword123",
            "email": "underage@example.com",
            "birthdate": "2010-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 403
        assert response.json()["message"] == "User must be at least 18 years old to register"

    def test_create_user_invalid_credit_card_format(self):
        """Test creating user with invalid credit card format"""
        user_data = {
            "username": "invalidcard",
            "password": "MyPassword123",
            "email": "card@example.com",
            "birthdate": "1990-01-01",
            "ccNumber": "123456789012345"  # 15 digits instead of 16
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Invalid credit card number format"

    def test_create_user_credit_card_with_letters(self):
        """Test creating user with credit card containing letters"""
        user_data = {
            "username": "lettercard",
            "password": "MyPassword123",
            "email": "letter@example.com",
            "birthdate": "1990-01-01",
            "ccNumber": "123456789012345a"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Invalid credit card number format"

class TestDeleteUser:
    def test_delete_user_exists(self):
        """Test deleting a user that exists"""
        test_user = User(
            username="todelete",
            password="hashedpass123",
            email="delete@example.com",
            birthdate="1990-01-01"
        )
        usersDB.append(test_user)
        
        response = client.delete("/users/delete/todelete")
        assert response.status_code == 200
        assert response.json()["message"] == "User deleted successfully"
        assert len(usersDB) == 0

    def test_delete_user_not_exists(self):
        """Test deleting a user that doesn't exist"""
        response = client.delete("/users/delete/nonexistent")
        assert response.status_code == 404
        assert response.json()["message"] == "User not found"

class TestPasswordHashing:
    def test_password_is_hashed_on_creation(self):
        """Test that password is hashed when user is created"""
        user_data = {
            "username": "hashuser",
            "password": "MyPassword123",
            "email": "hash@example.com",
            "birthdate": "1990-01-01"
        }
        
        response = client.post("/users/users/create", json=user_data)
        assert response.status_code == 201
        
        # Check that password in database is hashed (not plain text)
        assert usersDB[0].password != "MyPassword123"
        assert len(usersDB[0].password) == 64  # SHA-256 hash length


