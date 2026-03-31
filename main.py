from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Request(BaseModel):
    sequence: str
    pam: str = "NGG"


# OFF-TARGET
def count_similar(seq, guide):
    count = 0
    for i in range(len(seq) - len(guide)):
        window = seq[i:i+len(guide)]
        mismatch = sum(1 for a, b in zip(window, guide) if a != b)
        if mismatch <= 2:
            count += 1
    return count


def match_pam(seq, pam):
    for a, b in zip(seq, pam):
        if b != "N" and a != b:
            return False
    return True


@app.post("/api/analyze")
def analyze(req: Request):
    seq = req.sequence.upper()
    pam_type = req.pam.upper()

    if len(seq) < 23:
        return {"error": "Sequence too short"}

    results = []

    for i in range(len(seq) - 22):

        window = seq[i:i+23]

        # CASE 1: NGG (PAM at end)
        if pam_type == "NGG":
            spacer = window[:20]
            pam = window[-3:]

            if not match_pam(pam, pam_type):
                continue

        # CASE 2: TTTV (PAM at start)
        elif pam_type == "TTTV":
            pam = window[:4]
            spacer = window[4:24]

            if not match_pam(pam, pam_type):
                continue

        # CUSTOM PAM (assume end)
        else:
            pam_len = len(pam_type)
            spacer = window[:20]
            pam = window[-pam_len:]

            if not match_pam(pam, pam_type):
                continue

        gc = (spacer.count("G") + spacer.count("C")) / len(spacer) * 100

        score = 0

        if 40 <= gc <= 60:
            score += 20
        else:
            score -= 10

        if spacer[-1] == "G":
            score += 10

        if "TTTT" in spacer:
            score -= 10

        similar = count_similar(seq, spacer)

        if similar <= 1:
            risk = "SAFE"
        elif similar <= 3:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        results.append({
            "sequence": window,
            "score": score,
            "position": i,
            "gc": round(gc, 2),
            "risk": risk
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)

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
