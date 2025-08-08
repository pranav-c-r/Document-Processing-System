from fastapi import FastAPI
from routers import document_router
from fastapi.responses import JSONResponse

app = FastAPI()

# Register your router
app.include_router(document_router.router)

# Webhook route (matches what HackRx or Railway expects)
@app.post("/api/v1/hackrx/run")
def webhook():
    return JSONResponse(content={"message": "Webhook working!"})