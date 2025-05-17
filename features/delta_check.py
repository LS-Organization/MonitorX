import time
from collections import defaultdict
from utils.alert import send_alert

SETTLEMENTS = ["USDT", "USDC"]
THRESHOLD = 100 #$100
DELAY_SECONDS = 60 #sec
delta_exceed_start = {}

def extract_pairs(balance):
    grouped = defaultdict(list)
    for key in balance:
        for suffix in SETTLEMENTS:
            if key.endswith(suffix) and "Avg-Price" not in key:
                base = key.replace(suffix, "")
                grouped[base].append(key)
    return grouped

async def delta_check(account, balance):
    now = time.time()
    pairs = extract_pairs(balance)

    for base, symbols in pairs.items():
        if len(symbols) != 2:
            continue
        p1, p2 = symbols
        pos1 = balance.get(p1, 0)
        pos2 = balance.get(p2, 0)
        price = balance.get(f"{p1}Avg-Price", 0)
        if price == 0:
            continue
        v1 = abs(pos1 * price)
        v2 = abs(pos2 * price)
        delta = abs(v1 - v2)

        key = (account, *sorted([p1, p2]))
        if delta > THRESHOLD:
            if key not in delta_exceed_start:
                delta_exceed_start[key] = now
            elif now - delta_exceed_start[key] >= DELAY_SECONDS:
                msg = (
                    f"[{account}] {p1}/{p2} Δ=${delta:.2f} exceeded {THRESHOLD} for {DELAY_SECONDS}s\n"
                    f"• {p1}: {pos1} × {price} = ${v1:.2f}\n"
                    f"• {p2}: {pos2} × {price} = ${v2:.2f}"
                )
                send_alert(msg)
        else:
            delta_exceed_start.pop(key, None)

