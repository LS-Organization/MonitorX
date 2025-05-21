import time
from utils.alert import send_alert

imbalance_tracker = {}  # key: (account, sym1, sym2) → timestamp


def get_contract_size(symbol, contract_sizes):
    for base, sizes in contract_sizes.items():
        if base not in symbol:
            continue
        if "USDT" in symbol:
            return sizes.get("USDT")
        elif "USDC" in symbol:
            return sizes.get("USDC")
    return None


def find_usdt_usdc_pairs(balance, symbols_to_check):
    pairs = {}

    for key in balance:
        if "Avg-Price" in key or "Force-Liquid-Price" in key:
            continue

        for symbol in symbols_to_check:
            if symbol not in key:
                continue

            if "-USDC-SWAP" in key or "-USDT-SWAP" in key:
                base = key.replace("-USDC-SWAP", "").replace("-USDT-SWAP", "")
                pairs.setdefault(base, [None, None])
                if "USDC" in key:
                    pairs[base][0] = key
                else:
                    pairs[base][1] = key

            elif key.startswith("OKX-P-") and ("USDC" in key or "USDT" in key):
                base = key.replace("OKX-P-", "").replace("USDC", "").replace("USDT", "")
                if symbol not in base:
                    continue
                usdc_key = f"OKX-P-{base}USDC"
                usdt_key = f"OKX-P-{base}USDT"
                pairs.setdefault(f"OKX-P-{base}", [None, None])
                if "USDC" in key:
                    pairs[f"OKX-P-{base}"][0] = usdc_key
                else:
                    pairs[f"OKX-P-{base}"][1] = usdt_key

    return pairs


async def aaz_okx_hedge_check(context, params):
    account = params["account"]
    balance = context["accounts"].get(account)
    if not balance:
        return

    now = context["now"]
    threshold = params.get("threshold", 0)
    delay_seconds = params.get("delay", 5)
    symbols = params["symbols"]
    contract_sizes = params["contract_sizes"]

    pairs = find_usdt_usdc_pairs(balance, symbols)

    for base, (sym1, sym2) in pairs.items():
        if not sym1 or not sym2:
            continue

        size1 = get_contract_size(sym1, contract_sizes)
        size2 = get_contract_size(sym2, contract_sizes)
        if size1 is None or size2 is None:
            continue

        pos1 = balance.get(sym1, 0)
        pos2 = balance.get(sym2, 0)

        val1 = pos1 * size1
        val2 = pos2 * size2
        diff = val1 + val2

        usdt_sym = sym1 if "USDT" in sym1 else sym2
        avg_price = balance.get(f"{usdt_sym}Avg-Price", 0)
        usd_diff = abs(diff * avg_price)

        key = (account, sym1, sym2)

        if usd_diff > threshold:
            if key not in imbalance_tracker:
                imbalance_tracker[key] = now
            elif now - imbalance_tracker[key] >= delay_seconds:
                msg = f"""
[{account}] {sym1} / {sym2} Δ=${usd_diff:.2f} > {threshold} for {delay_seconds}s

• {sym1:<20} {pos1:.4f} × size={size1:.4f} = {val1:.4f}  
• {sym2:<20} {pos2:.4f} × size={size2:.4f} = {val2:.4f}  
•  Δ== {diff:.4f} × ${avg_price:.2f} = Δ ${usd_diff:.2f}
"""
                send_alert(msg)
        else:
            imbalance_tracker.pop(key, None)