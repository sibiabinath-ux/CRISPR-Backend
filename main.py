from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS FIX (VERY IMPORTANT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all requests (Netlify → Render)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class Request(BaseModel):
    sequence: str

# API endpoint
@app.post("/api/analyze")
def analyze(req: Request):
    seq = req.sequence.upper()

    # Basic validation
    if len(seq) < 23:
        return {
            "message": "Sequence too short",
            "length": len(seq)
        }

    return {
        "message": "Backend working ✅",
        "length": len(seq)
    }
