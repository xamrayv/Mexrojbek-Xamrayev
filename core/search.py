import re
from difflib import SequenceMatcher


def score(query, text):
    """0 = mos emas. Qancha katta bo'lsa, shuncha o'xshash."""
    q = query.casefold().strip()
    t = text.casefold()
    if not q:
        return 0
    if t == q:
        return 100
    if t.startswith(q):
        return 90
    if q in t:
        return 80
    words = [w for w in re.split(r"\W+", t) if w] + [t]
    best = max(SequenceMatcher(None, q, w).ratio() for w in words)
    return int(best * 70) if best >= 0.6 else 0


def rank(items, query, key):
    """(mos kelganlar, qolganlar) qaytaradi. Mos kelganlar o'xshashligi bo'yicha tartiblanadi."""
    scored = [(score(query, key(i)), i) for i in items]
    hits = sorted((x for x in scored if x[0] > 0), key=lambda x: -x[0])
    matched = [i for _, i in hits]
    rest = [i for s, i in scored if s == 0]
    for i in matched:
        i.hit = True
    return matched, rest
