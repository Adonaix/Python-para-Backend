from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
def test():
    return {"nombre": "Abdul"}



