import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.storage import paymentsDB, usersDB
from app.models import Payment, User

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    """Clear the database before each test"""
    paymentsDB.clear()
    usersDB.clear()
    yield

class TestGetPayments:
    def test_get_all_payments_empty(self):
        """Test getting all payments when database is empty"""
        response = client.get("/payments/getAll")
        assert response.status_code == 200
        assert response.json() == {"payments": []}

    def test_get_all_payments_with_data(self):
        """Test getting all payments when database has data"""
        # Add test payments
        payment1 = Payment(id=1, ccNumber="1234567890123456", amount=100, date="2024-01-01T10:00:00")
        payment2 = Payment(id=2, ccNumber="6543210987654321", amount=200, date="2024-01-02T10:00:00")
        paymentsDB.extend([payment1, payment2])
        
        response = client.get("/payments/getAll")
        assert response.status_code == 200
        payments = response.json()["payments"]
        assert len(payments) == 2
        assert payments[0]["amount"] == 100
        assert payments[1]["amount"] == 200

class TestGetPaymentById:
    def test_get_payment_by_id_exists(self):
        """Test getting a payment that exists"""
        payment = Payment(id=1, ccNumber="1234567890123456", amount=100, date="2024-01-01T10:00:00")
        paymentsDB.append(payment)
        
        response = client.get("/payments/getPaymentById/1")
        assert response.status_code == 200
        assert response.json()["payment"]["id"] == 1

    def test_get_payment_by_id_not_exists(self):
        """Test getting a payment that doesn't exist"""
        response = client.get("/payments/getPaymentById/999")
        assert response.status_code == 404
        assert response.json()["message"] == "Payment not found"

class TestCreatePayment:
    def test_create_payment_success(self):
        """Test creating a payment with valid data"""
        # First create a user with a credit card
        user = User(
            username="testuser",
            password="hashedpass123",
            email="test@example.com",
            birthdate="1990-01-01",
            ccNumber="1234567890123456"
        )
        usersDB.append(user)
        
        payment_data = {
            "ccNumber": "1234567890123456",
            "amount": 150
        }
        
        response = client.post("/payments/create", json=payment_data)
        assert response.status_code == 201
        assert response.json()["message"] == "Payment created successfully"
        
        # Check if payment was added to database
        assert len(paymentsDB) == 1
        assert paymentsDB[0].amount == 150
        assert paymentsDB[0].id == 1

    def test_create_payment_invalid_card_format(self):
        """Test creating payment with invalid credit card format"""
        payment_data = {
            "ccNumber": "123456789012345",  # 15 digits instead of 16
            "amount": 100
        }
        
        response = client.post("/payments/create", json=payment_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Card number must be numeric and 16 digits long"

    def test_create_payment_invalid_amount_too_small(self):
        """Test creating payment with amount less than 100"""
        # Register a user so card is known
        usersDB.append(User(
            username="amountsmall",
            password="hashedpass123",
            email="small@example.com",
            birthdate="1990-01-01",
            ccNumber="1234567890123456"
        ))
        payment_data = {
            "ccNumber": "1234567890123456",
            "amount": 99
        }
        
        response = client.post("/payments/create", json=payment_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Amount must be exactly 3 digits (100-999)"

    def test_create_payment_invalid_amount_too_large(self):
        """Test creating payment with amount more than 999"""
        # Register a user so card is known
        usersDB.append(User(
            username="amountlarge",
            password="hashedpass123",
            email="large@example.com",
            birthdate="1990-01-01",
            ccNumber="1234567890123456"
        ))
        payment_data = {
            "ccNumber": "1234567890123456",
            "amount": 1000
        }
        
        response = client.post("/payments/create", json=payment_data)
        assert response.status_code == 400
        assert response.json()["message"] == "Amount must be exactly 3 digits (100-999)"

    def test_create_payment_unregistered_card(self):
        """Test creating payment with unregistered credit card"""
        payment_data = {
            "ccNumber": "1234567890123456",
            "amount": 100
        }
        
        response = client.post("/payments/create", json=payment_data)
        assert response.status_code == 404
        assert response.json()["message"] == "Card number is not registered to any user"

    def test_create_payment_auto_increment_id(self):
        """Test that payment IDs auto-increment correctly"""
        # First create a user with a credit card
        user = User(
            username="testuser",
            password="hashedpass123",
            email="test@example.com",
            birthdate="1990-01-01",
            ccNumber="1234567890123456"
        )
        usersDB.append(user)
        
        # Create first payment
        payment_data1 = {
            "ccNumber": "1234567890123456",
            "amount": 100
        }
        response1 = client.post("/payments/create", json=payment_data1)
        assert response1.status_code == 201
        
        # Create second payment
        payment_data2 = {
            "ccNumber": "1234567890123456",
            "amount": 200
        }
        response2 = client.post("/payments/create", json=payment_data2)
        assert response2.status_code == 201
        
        # Check IDs are incremented
        assert len(paymentsDB) == 2
        assert paymentsDB[0].id == 1
        assert paymentsDB[1].id == 2

class TestDeletePayment:
    def test_delete_payment_exists(self):
        """Test deleting a payment that exists"""
        payment = Payment(id=1, ccNumber="1234567890123456", amount=100, date="2024-01-01T10:00:00")
        paymentsDB.append(payment)
        
        response = client.delete("/payments/delete/1")
        assert response.status_code == 200
        assert response.json()["message"] == "Payment deleted successfully"
        assert len(paymentsDB) == 0

    def test_delete_payment_not_exists(self):
        """Test deleting a payment that doesn't exist"""
        response = client.delete("/payments/delete/999")
        assert response.status_code == 404
        assert response.json()["message"] == "Payment not found"
