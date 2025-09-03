from datetime import datetime
import re
import hashlib

from app.models import Payment, User
from .storage import usersDB, paymentsDB

    
def checkUsernameUnique(username: str) -> bool:
    """Check if the username is unique in the usersDB"""
    existingUsernames = [u.username for u in usersDB]
    return username not in existingUsernames

def validateUsernameAlphanumeric(username: str) -> bool:
    """Check if the username is alphanumeric"""
    return username.isalnum()

def validatePasswordChars(password: str) -> bool:
    """Check if the password contains at least one uppercase letter and one number"""
    return (any(c.isupper() for c in password) and any(c.isdigit() for c in password))

def validatePasswordLength(password: str) -> bool:
    """Check if the password length is at least 8 characters"""
    return len(password) >= 8

def validateEmail(email: str) -> bool:
    """Validate the email format using regex"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def validateDateFormat(date_str: str) -> bool:
    """Validate that the date is in ISO 8601 format (YYYY-MM-DD)"""
    return re.match(r'^\d{4}-\d{2}-\d{2}$', date_str) is not None

def checkAgeEligibility(birthdate: str) -> bool:
    """Check if the user is at least 18 years old based on birthdate in YYYY-MM-DD format"""
    if not validateDateFormat(birthdate):
        return False
    birth_date = datetime.strptime(birthdate, "%Y-%m-%d")
    age = (datetime.now() - birth_date).days // 365
    return age >= 18

def validateCreditCard(ccNumber: str) -> bool:
    """Validate that the credit card number is numeric and 16 digits long"""
    return re.match(r'^\d{16}$', ccNumber) is not None

def checkCardRegistered(ccNumber: str) -> bool:
    """Check if the credit card number is registered to any user"""
    for user in usersDB:
        if user.ccNumber == ccNumber:
            return True
    return False

def validateAmount(amount: int) -> bool:
    """Validate that the amount is exactly 3 digits (100-999)"""
    return 100 <= amount <= 999

def hashPassword(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()