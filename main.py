from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/afc/api")
async def api():
    return {"message": "API Endpoint"}