from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS (REQUIRED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    sequence: str

@app.post("/api/analyze")
def analyze(req: Request):
    seq = req.sequence.upper()

    if len(seq) < 23:
        return {"error": "Sequence too short"}

    results = []

    for i in range(len(seq) - 22):
        guide = seq[i:i+23]
        spacer = guide[:20]
        pam = guide[-3:]

        # PAM check (NGG)
        if pam[1:] != "GG":
            continue

        gc = (spacer.count("G") + spacer.count("C")) / 20 * 100

        score = 0

        # GC scoring
        if 40 <= gc <= 60:
            score += 20
        else:
            score -= 10

        # Position rules
        if spacer[-1] == "G":
            score += 10

        if "TTTT" in spacer:
            score -= 10

        results.append({
            "sequence": guide,
            "score": score,
            "position": i,
            "gc": round(gc, 2)
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    return {
        "count": len(results),
        "top": results[:10]
    }
