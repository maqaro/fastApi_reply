# Streamly Video Streaming API

A production-quality API for a video streaming service that handles user registration and payment processing.

## Prerequisites
- Python 3.8+
- Pip

## Installation & Setup

1. **Clone the repository:**
```bash
git clone https://github.com/maqaro/fastApi_reply
cd fastApi_reply
```

2. **Create and activate a virtual environment (optional but recommended):**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows PowerShell
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
uvicorn app.main:app --reload
```

5. **Access the API:**
- API Base URL: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Running Tests

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_main.py -v
pytest tests/test_users.py -v
pytest tests/test_payments.py -v
```

## Features

- **User Registration Service** (`/users` endpoint)
- **Payment Service** (`/payments` endpoint)
- **Comprehensive validation** for all inputs
- **In-memory data storage** using Python data structures
- **Full unit test coverage**

## API Endpoints

### Users Service (`/users`)

#### POST `/users/users/create`
Creates a new user account.

**Request Body:**
```json
{
    "username": "alicesmith",
    "password": "MyPassword123",
    "email": "alice.smith@streamly.com",
    "birthdate": "1985-12-25",
    "ccNumber": "4532123456789012"
}
```

**Validations:**
- Username: Must be alphanumeric, no spaces
- Password: Minimum 8 characters, must include uppercase letter and number
- Email: Must be valid email format
- Date of Birth: Must be in ISO 8601 format (YYYY-MM-DD)
- Credit Card: Optional, must be exactly 16 digits if provided
- Age: Must be at least 18 years old

**Response Codes:**
- `201`: User created successfully
- `400`: Validation checks failed
- `403`: User under 18 years old
- `409`: Username already exists

#### GET `/users/getAll`
Retrieves all users with optional filtering.

**Query Parameters:**
- `creditcard`: Filter by credit card status (`yes`/`no`)

**Examples:**
- `GET /users/getAll` - Returns all users
- `GET /users/getAll?creditcard=yes` - Returns users with credit cards
- `GET /users/getAll?creditcard=no` - Returns users without credit cards

#### GET `/users/getByUsername/{username}`
Retrieves a specific user by username.

**Response Codes:**
- `200`: User found
- `404`: User not found

#### DELETE `/users/delete/{username}`
Deletes a user by username.

**Response Codes:**
- `200`: User deleted successfully
- `404`: User not found

### Payments Service (`/payments`)

#### POST `/payments/create`
Creates a new payment.

**Request Body:**
```json
{
    "ccNumber": "4532123456789012",
    "amount": 150
}
```

**Validations:**
- Credit Card Number: Must be exactly 16 digits
- Amount: Must be exactly 3 digits (100-999)
- Credit Card must be registered to an existing user

**Response Codes:**
- `201`: Payment created successfully
- `400`: Validation checks failed
- `404`: Credit card not registered to any user

#### GET `/payments/getAll`
Retrieves all payments.

#### GET `/payments/getPaymentById/{payment_id}`
Retrieves a specific payment by ID.

**Response Codes:**
- `200`: Payment found
- `404`: Payment not found

#### DELETE `/payments/delete/{payment_id}`
Deletes a payment by ID.

**Response Codes:**
- `200`: Payment deleted successfully
- `404`: Payment not found

## Data Storage

The application uses in-memory Python data structures for data storage:
- `usersDB`: List of User objects
- `paymentsDB`: List of Payment objects

**Note:** Data is not persisted between application restarts.

## Technical Implementation

- **Framework**: FastAPI
- **Language**: Python 3.8+
- **Testing**: pytest with httpx
- **Data Models**: Pydantic BaseModel
- **Validation**: Custom validation functions with regex patterns
- **Password Security**: SHA-256 hashing

## Production Quality Features

- Comprehensive input validation
- Proper HTTP status codes
- Detailed error messages
- Full unit test coverage
- Clean code structure and separation of concerns
- API documentation with OpenAPI/Swagger
- Type hints and Pydantic models
- Proper exception handling

## API Examples

### Create a User
```bash
curl -X POST "http://localhost:8000/users/users/create" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johnsmith",
       "password": "SecurePass123",
       "email": "john@example.com",
       "birthdate": "1990-05-15"
     }'
```

### Create a Payment
```bash
curl -X POST "http://localhost:8000/payments/create" \
     -H "Content-Type: application/json" \
     -d '{
       "ccNumber": "4532123456789012",
       "amount": 250
     }'
```

### Get All Users with Credit Cards
```bash
curl "http://localhost:8000/users/getAll?creditcard=yes"
```
