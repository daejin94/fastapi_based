from fastapi import FastAPI

app = FastAPI(title="Backend API")

@app.get("/")
def health_check():
    return {"status": "ok"}