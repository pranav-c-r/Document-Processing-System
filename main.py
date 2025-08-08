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
if __name__ == "__main__":
    import uvicorn
    import os

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
