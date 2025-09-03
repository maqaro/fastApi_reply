from pydantic import BaseModel, ConfigDict
from typing import Optional

class User(BaseModel):
    username: str
    password: str
    email: str
    birthdate: str
    ccNumber: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "alicesmith",
                    "password": "MyPassword123",
                    "email": "alice.smith@streamly.com",
                    "birthdate": "1985-12-25",
                    "ccNumber": "4532123456789012"
                }
            ]
        }
    )

class Payment(BaseModel):
    id: Optional[int] = 0
    ccNumber: str
    amount: int
    date: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "ccNumber": "4532123456789012",
                    "amount": 100
                }
            ]
        }
    )
