import datetime
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from ..models import Payment
from ..storage import paymentsDB
from ..utils import checkCardRegistered, validateCreditCard, validateAmount

router = APIRouter(
    prefix="/payments"
)

@router.get("/getAll", tags=["Payments"])
def get_payments():
    """Get all payments"""
    return {"payments": [payment.model_dump() for payment in paymentsDB]}

@router.get("/getPaymentById/{payment_id}", tags=["Payments"], response_model=dict,
             responses=
             {
                200: {"description": "Payment Found Successfully"},
                404: {"description": "Payment Not Found"}
             })
def get_payment_by_id(payment_id: int):
    """Get a payment by ID"""
    for payment in paymentsDB:
        if payment.id == payment_id:
            return JSONResponse(status_code=200, content={"payment": payment.model_dump()})
    return JSONResponse(status_code=404, content={"message": "Payment not found"})

@router.post(
        "/create", tags=["Payments"], response_model=dict, 
        responses=
            {
            201: {"description": "Created Successfully"}, 
            400: {"description": "Validation Checks Failed"}, 
            404: {"description": "Card Number Not Registered"}
        }
    )
def createPayment(payment: Payment):
    """Create a new payment after completing all validation checks"""
    # check if card number is numeric and 16 digits
    if not validateCreditCard(payment.ccNumber):
        return JSONResponse(status_code=400, content={"message": "Card number must be numeric and 16 digits long"})

    # Check if card number is registered to any user
    elif not checkCardRegistered(payment.ccNumber):
        return JSONResponse(status_code=404, content={"message": "Card number is not registered to any user"})

    # Check if amount is exactly 3 digits (100-999)
    elif not validateAmount(payment.amount):
        return JSONResponse(status_code=400, content={"message": "Amount must be exactly 3 digits (100-999)"})

    last_id = paymentsDB[-1].id if paymentsDB and paymentsDB[-1].id is not None else 0
    new_payment = Payment(ccNumber=payment.ccNumber, amount=payment.amount, date=datetime.datetime.now().isoformat(), id=last_id + 1)
    paymentsDB.append(new_payment)
    return JSONResponse(status_code=201, content={"message": "Payment created successfully", "payment": new_payment.model_dump()})

@router.delete("/delete/{payment_id}", tags=["Payments"], response_model=dict,
                responses=
                {
                    200: {"description": "Deleted Successfully"},
                    404: {"description": "Payment Not Found"}
                }
            )
def delete_payment(payment_id: int):
    """Delete a payment by ID"""
    for payment in paymentsDB:
        if payment.id == payment_id:
            paymentsDB.remove(payment)
            return JSONResponse(status_code=200, content={"message": "Payment deleted successfully"})
    return JSONResponse(status_code=404, content={"message": "Payment not found"})
