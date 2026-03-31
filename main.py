from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (important)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    sequence: str


# 🔥 OFF-TARGET SIMULATION
def count_similar(seq, guide):
    count = 0

    for i in range(len(seq) - len(guide)):
        window = seq[i:i+len(guide)]

        mismatch = sum(1 for a, b in zip(window, guide) if a != b)

        if mismatch <= 2:
            count += 1

    return count


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

        # PAM check
        if pam[1:] != "GG":
            continue

        gc = (spacer.count("G") + spacer.count("C")) / 20 * 100

        score = 0

        if 40 <= gc <= 60:
            score += 20
        else:
            score -= 10

        if spacer[-1] == "G":
            score += 10

        if "TTTT" in spacer:
            score -= 10

        # 🔥 OFF-TARGET
        similar = count_similar(seq, spacer)

        if similar <= 1:
            risk = "SAFE"
        elif similar <= 3:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        results.append({
            "sequence": guide,
            "score": score,
            "position": i,
            "gc": round(gc, 2),
            "risk": risk
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    # BEST SAFE GUIDE
    best = None
    for r in results:
        if r["risk"] == "SAFE" and 40 <= r["gc"] <= 60:
            best = r
            break

    if not best and results:
        best = results[0]

    return {
        "count": len(results),
        "top": results[:10],
        "best": best
    }
