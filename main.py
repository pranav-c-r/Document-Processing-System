# app/main.py

from fastapi import FastAPI
from routers import document_router

app = FastAPI()

# Add your router (API route)
app.include_router(document_router.router)

@app.post("/webhook")
def home():
    return {"message": "Document Processing API is up!"}
