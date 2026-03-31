from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Request(BaseModel):
    sequence: str

@app.post("/api/analyze")
def analyze(req: Request):
    seq = req.sequence.upper()

    return {
        "message": "Backend working",
        "length": len(seq)
    }
