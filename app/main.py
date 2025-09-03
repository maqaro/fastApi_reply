from fastapi import FastAPI
from .routes.users import router as usersRouter
from .routes.payments import router as paymentsRouter

app = FastAPI()

# Include the users router
app.include_router(usersRouter)
app.include_router(paymentsRouter)

@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to Streamly API", "docs": "/docs"}