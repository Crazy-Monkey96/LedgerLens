"""
Synthetic transaction generator for LedgerLens.

Produces realistic, noisy, and deliberately AMBIGUOUS merchant strings labelled
by category. Ambiguity is intentional: several merchants legitimately span
categories (AMAZON -> shopping/groceries/entertainment; UPI/PAYTM -> transfer/
income/other), and a small fraction of labels are flipped to mimic real
mislabelling. This makes the categorisation task non-trivial, so model quality
is a real signal rather than a toy 100%.

Everything here is SYNTHETIC and must be reported as such.
"""
from __future__ import annotations
import argparse
import csv
import random
from datetime import date, timedelta

# Unambiguous, category-specific merchants
SPECIFIC: dict[str, list[str]] = {
    "groceries":     ["TESCO", "SAINSBURYS", "ALDI", "LIDL", "BIGBASKET", "DMART"],
    "dining":        ["STARBUCKS", "DOMINOS", "MCDONALDS", "SWIGGY", "ZOMATO", "CAFE COFFEE DAY"],
    "transport":     ["UBER", "OLA", "SHELL", "BP FUEL", "IRCTC", "METRO CARD"],
    "utilities":     ["VODAFONE", "AIRTEL", "BSES POWER", "ACT FIBERNET", "GAS BILL"],
    "rent":          ["RENT PAYMENT", "LANDLORD TRANSFER", "HOUSING SOCIETY"],
    "entertainment": ["NETFLIX", "SPOTIFY", "PVR CINEMAS", "STEAM", "PRIME VIDEO"],
    "health":        ["APOLLO PHARMACY", "1MG", "PRACTO", "FITNESS FIRST"],
    "shopping":      ["MYNTRA", "IKEA", "H&M", "FLIPKART"],
    "income":        ["SALARY CREDIT", "PAYROLL", "STIPEND"],
    "transfer":      ["NEFT", "IMPS", "SELF TRANSFER"],
    "other":         ["MISC DEBIT", "SERVICE CHARGE", "ATM WITHDRAWAL", "UNKNOWN"],
}

# Ambiguous merchants: each maps to a DISTRIBUTION over plausible categories.
AMBIGUOUS: list[tuple[str, dict[str, float]]] = [
    ("AMAZON",        {"shopping": 0.6, "groceries": 0.2, "entertainment": 0.2}),
    ("PAYTM",         {"transfer": 0.4, "shopping": 0.3, "utilities": 0.3}),
    ("UPI TRANSFER",  {"transfer": 0.5, "income": 0.25, "other": 0.25}),
    ("PHONEPE",       {"transfer": 0.4, "dining": 0.3, "shopping": 0.3}),
    ("GOOGLE",        {"entertainment": 0.5, "utilities": 0.3, "other": 0.2}),
    ("APPLE.COM/BILL",{"entertainment": 0.6, "shopping": 0.4}),
    ("RELIANCE",      {"groceries": 0.5, "utilities": 0.5}),
    ("CARD PAYMENT",  {"other": 0.5, "shopping": 0.3, "transfer": 0.2}),
]

AMOUNTS = {
    "groceries": (-90, -8), "dining": (-40, -5), "transport": (-60, -3),
    "utilities": (-120, -15), "rent": (-1500, -400), "entertainment": (-30, -5),
    "health": (-80, -5), "shopping": (-200, -10), "income": (800, 3000),
    "transfer": (-500, 500), "other": (-100, -5),
}
NOISE = ["", " #{}", " REF{}", " *{}", " TXN{}", " /{}", " POS {}"]


def noisy(name: str, rng: random.Random) -> str:
    s = name
    if rng.random() < 0.5:
        s += NOISE[rng.randrange(len(NOISE))].format(rng.randint(100, 9999))
    if rng.random() < 0.3:
        s += " " + rng.choice(["LONDON", "MUMBAI", "DELHI", "BATH GB", "ONLINE"])
    if rng.random() < 0.2:
        s = s.lower()
    return s


def generate(rows: int, seed: int, label_noise: float = 0.03):
    rng = random.Random(seed)
    cats = list(SPECIFIC)
    weights = [8, 7, 6, 4, 2, 3, 3, 6, 2, 5, 3]
    start = date.today() - timedelta(days=365)

    for i in range(rows):
        if rng.random() < 0.35:  # 35% ambiguous merchants
            merchant, dist = rng.choice(AMBIGUOUS)
            cat = rng.choices(list(dist), weights=list(dist.values()))[0]
            desc = noisy(merchant, rng)
        else:
            cat = rng.choices(cats, weights=weights)[0]
            desc = noisy(rng.choice(SPECIFIC[cat]), rng)

        label = cat
        if rng.random() < label_noise:          # realistic mislabelling
            label = rng.choice(cats)

        lo, hi = AMOUNTS[cat]
        amount = round(rng.uniform(lo, hi), 2)
        d = start + timedelta(days=rng.randint(0, 365))
        yield {"date": d.isoformat(), "description": desc, "amount": amount, "category": label}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rows", type=int, default=20000)
    p.add_argument("--out", required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--label-noise", type=float, default=0.03)
    args = p.parse_args()
    import os
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", "description", "amount", "category"])
        w.writeheader()
        for row in generate(args.rows, args.seed, args.label_noise):
            w.writerow(row)
    print(f"Wrote {args.rows} synthetic transactions -> {args.out}")


if __name__ == "__main__":
    main()
