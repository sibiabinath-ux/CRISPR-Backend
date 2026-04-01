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


# 🔁 Reverse complement
def reverse_complement(seq):
    complement = {"A":"T","T":"A","C":"G","G":"C"}
    return "".join(complement.get(b, b) for b in reversed(seq))


def match_pam(seq, pam):
    for a, b in zip(seq, pam):
        if b != "N" and a != b:
            return False
    return True


def scan_sequence(seq, pam_type, strand_label):

    results = []
    n = len(seq)

    for i in range(n - 23):

        window = seq[i:i+23]

        if pam_type == "NGG":
            spacer = window[:20]
            pam = window[-3:]

        elif pam_type == "TTTV":
            pam = window[:4]
            spacer = window[4:24]

        else:
            pam_len = len(pam_type)
            spacer = window[:20]
            pam = window[-pam_len:]

        if not match_pam(pam, pam_type):
            continue

        gc = (spacer.count("G") + spacer.count("C")) * 5

        score = 0

        if 40 <= gc <= 60:
            score += 20
        else:
            score -= 10

        if spacer[-1] == "G":
            score += 10

        if "TTTT" in spacer:
            score -= 10

        if gc < 40:
            risk = "HIGH"
        elif gc > 65:
            risk = "MEDIUM"
        else:
            risk = "SAFE"

        results.append({
            "sequence": window,
            "score": score,
            "position": i,
            "gc": gc,
            "risk": risk,
            "strand": strand_label
        })

    return results


@app.post("/api/analyze")
def analyze(req: Request):

    seq = req.sequence.upper()
    pam_type = req.pam.upper()

    if len(seq) < 23:
        return {"error": "Sequence too short"}

    # Forward
    forward_results = scan_sequence(seq, pam_type, "+")

    # Reverse
    rev_seq = reverse_complement(seq)
    reverse_results = scan_sequence(rev_seq, pam_type, "-")

    results = forward_results + reverse_results

    results.sort(key=lambda x: x["score"], reverse=True)

    best = None
    for r in results:
        if r["risk"] == "SAFE":
            best = r
            break

    if not best and results:
        best = results[0]

    return {
        "count": len(results),
        "top": results[:10],
        "best": best,
        "all": results
    }
