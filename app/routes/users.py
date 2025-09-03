from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from ..utils import *
from ..models import User
from ..storage import usersDB
from typing import Optional

router = APIRouter(
    prefix="/users"
)

@router.get("/getAll", tags=["Users"])
def get_users(creditcard: Optional[str] = Query(None, description="Filter by credit card: 'yes' or 'no'")):
    """Get all users with optional credit card filter"""
    filtered_users = usersDB
    
    if creditcard:
        creditcard_lower = creditcard.lower()
        if creditcard_lower == "yes":
            # Filter users who have a credit card (ccNumber is not None and not empty)
            filtered_users = [user for user in usersDB if user.ccNumber is not None and user.ccNumber.strip() != ""]
        elif creditcard_lower == "no":
            # Filter users who don't have a credit card (ccNumber is None or empty)
            filtered_users = [user for user in usersDB if user.ccNumber is None or user.ccNumber.strip() == ""]
        else:
            return JSONResponse(status_code=400, content={"message": "Invalid creditcard filter. Use 'yes' or 'no'"})
    return {"users": [user.model_dump() for user in filtered_users]}

@router.get("/getByUsername/{username}", tags=["Users"], response_model=dict, responses={404: {"description": "User Not Found"}})
def get_user_by_username(username: str):
    """Get a user by username"""
    for user in usersDB:
        if user.username == username:
            return {"user": user.model_dump()}
    return JSONResponse(status_code=404, content={"message": "User not found"})

@router.post(
        "/users/create", tags=["Users"], response_model=dict, 
        responses=
            {
            201: {"description": "Created Successfully"}, 
            400: {"description": "Validation Checks Failed"}, 
            403: {"description": "Forbidden"}, 
            409: {"description": "Username Conflict"}
        }
    )
def create_user(user: User):
    """Create a new user after completing all validation checks"""
    # check if username is alphanumeric
    if not validateUsernameAlphanumeric(user.username):
        return JSONResponse(status_code=400, content={"message": "Username must be alphanumeric"})

    # Check if username already exists
    elif not checkUsernameUnique(user.username):
        return JSONResponse(status_code=409, content={"message": "Username already exists"})

    # check if password length is at least 8 characters
    elif not validatePasswordLength(user.password):
        return JSONResponse(status_code=400, content={"message": "Password must be at least 8 characters long"})

    # check if password contains at least one uppercase letter and one number
    elif not validatePasswordChars(user.password):
        return JSONResponse(status_code=400, content={"message": "Password must include at least 1 uppercase letter and 1 number"})
    
    # Validate email format
    elif not validateEmail(user.email):
        return JSONResponse(status_code=400, content={"message": "Invalid email format"})
    
    # Validate that DOB is in ISO 8691 format
    elif not validateDateFormat(user.birthdate):
        return JSONResponse(status_code=400, content={"message": "Birthdate must be in YYYY-MM-DD format"})
    
    # Validate that user is at least 18 years old
    elif not checkAgeEligibility(user.birthdate):
        return JSONResponse(status_code=403, content={"message": "User must be at least 18 years old to register"})
    
    # If credit card number is provided, validate its format (simple check for digits and length)
    elif user.ccNumber and not validateCreditCard(user.ccNumber):
        return JSONResponse(status_code=400, content={"message": "Invalid credit card number format"})
    
    # All validations passed, create and store the user
    else:
        newUser = User(
            username=user.username,
            password=hashPassword(user.password),
            email=user.email,
            birthdate=user.birthdate,
            ccNumber=user.ccNumber
        )

        usersDB.append(newUser)

    return JSONResponse(status_code=201, content={"message": "User created successfully", "user": newUser.model_dump()})

@router.delete("/delete/{username}", tags=["Users"], response_model=dict, responses={404: {"description": "User Not Found"}})
def delete_user(username: str):
    """Delete a user by username"""
    for i, user in enumerate(usersDB):
        if user.username == username:
            del usersDB[i]
            return {"message": "User deleted successfully"}
    return JSONResponse(status_code=404, content={"message": "User not found"})