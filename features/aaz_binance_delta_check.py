import time
from collections import defaultdict
from utils.alert import send_alert

delta_exceed_start = {}
last_alert_time = {}

async def aaz_binance_delta_check(context, params):
    account = params["account"]
    balance = context["accounts"].get(account)
    if not balance:
        return

    threshold = params.get("threshold", 100)
    delay_seconds = params.get("delay", 60)
    cooldown_seconds = params.get("cooldown", 300)  #cooldown for 5 minutes
    now = context["now"]

    grouped = defaultdict(list)
    for key in balance:
        if key.endswith("Avg-Price"):
            continue
        for suffix in ["USDT", "USDC"]:
            if key.endswith(suffix):
                base = key.replace(suffix, "")
                grouped[base].append(key)

    for base, pairs in grouped.items():
        if len(pairs) != 2:
            continue
        p1, p2 = pairs
        pos1 = balance.get(p1, 0)
        pos2 = balance.get(p2, 0)
        price = balance.get(f"{p1}Avg-Price", 0)
        if price == 0:
            continue

        v1 = abs(pos1 * price)
        v2 = abs(pos2 * price)
        delta = abs(v1 - v2)

        key = (account, p1, p2)

        if delta > threshold:
            if key not in delta_exceed_start:
                delta_exceed_start[key] = now
            elif now - delta_exceed_start[key] >= delay_seconds:
                last_sent = last_alert_time.get(key, 0)
                if now - last_sent >= cooldown_seconds:
                    msg = f"""
[{account}] {p1} / {p2} Δ = ${delta:.2f} > {threshold} for {delay_seconds}s

• {p1:<10} {pos1:.2f} × {price:.4f} = ${v1:.2f}  
• {p2:<10} {pos2:.2f} × {price:.4f} = ${v2:.2f}
"""
                    send_alert(msg)
                    last_alert_time[key] = now
        else:
            delta_exceed_start.pop(key, None)
            last_alert_time.pop(key, None) 
