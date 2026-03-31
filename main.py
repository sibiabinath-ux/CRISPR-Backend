# Sort results
results = sorted(results, key=lambda x: x["score"], reverse=True)

# Always pick BEST = top result (safe fallback)
best = results[0] if results else None

# Improve: prefer safe GC if available
for r in results:
    if 40 <= r["gc"] <= 60:
        best = r
        break

return {
    "count": len(results),
    "top": results[:10],
    "best": best
}
