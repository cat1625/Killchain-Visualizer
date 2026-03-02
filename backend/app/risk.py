PHISHY_WORDS = ["urgent","immediately","transfer","invoice","password","verify","click","login","bank"]

def score_email(event: dict) -> float:
    score = 0.0
    subj = (event.get('subject') or "").lower()
    body = (event.get('body') or "").lower()

    for w in PHISHY_WORDS:
        if w in subj or w in body:
            score += 0.15

    if event.get('urls'):
        score += 0.3

    # domain count
    if len(event.get('domains', [])) >= 2:
        score += 0.1

    return min(1.0, score)
