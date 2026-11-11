"""
This file returns an explanation for the top offer and why it was the highest ranked.
"""

STRONG = 75 
WEAK = 40

def describe_criterion(name, offer, score, profile):
    """Return a phrase about one criterion that completes a sentence starting with 'it'."""
    h, m = divmod(offer.duration_minutes, 60)

    if name == "price":
        if score >= STRONG:
            return f"is very affordable at €{offer.price:.2f}"
        if score >= WEAK:
            return f"is reasonably priced at €{offer.price:.2f}"
        return f"is expensive at €{offer.price:.2f}"

    if name == "duration":
        if score >= STRONG:
            return f"has a short journey of {h}h {m:02d}m"
        if score >= WEAK:
            return f"has a reasonable journey of {h}h {m:02d}m"
        return f"has a long journey of {h}h {m:02d}m"

    if name == "departure_time":
        pref = f"{profile.preferred_departure:%H:%M}"
        dep = f"{offer.departure:%H:%M}"
        if score >= STRONG:
            return f"departs at {dep}, close to your preferred {pref}"
        if score >= WEAK:
            return f"departs at {dep}, reasonably close to your preferred {pref}"
        return f"departs at {dep}, far from your preferred {pref}"

    if name == "flexibility":
        if score >= STRONG:
            return "has a fully flexible fare (changeable and refundable)"
        if score >= WEAK:
            return "has a partly flexible fare"
        return "has a restrictive fare"

    return f"scores {score:.1f} on {name}"

def explain_offer(offer, total_score, scores, profile):
    strengths = [n for n, s in scores.items() if s >= STRONG]
    weaknesses = [n for n, s in scores.items() if s < WEAK]
    decisive = max(scores, key=lambda n: profile.weights[n] * scores[n])

    lines = [f"{offer.company.name} (offer {offer.offer_id}) ranks highest for "
             f"{profile.name} with a total score of {total_score:.1f}."]
    lines.append(f"The deciding factor: it {describe_criterion(decisive, offer, scores[decisive], profile)}.")
    for n in strengths:
        if n != decisive:
            lines.append(f"Strength: it {describe_criterion(n, offer, scores[n], profile)}.")
    for n in weaknesses:
        lines.append(f"Drawback: it {describe_criterion(n, offer, scores[n], profile)}.")
    
    if not weaknesses:
        weakest = min(scores, key=scores.get)
        lines.append(f"Weakest point: it {describe_criterion(weakest, offer, scores[weakest], profile)}.")

    lines.append("This is the best match under the selected weights, "
                 "not an objectively best offer.")
    return "\n".join(lines)