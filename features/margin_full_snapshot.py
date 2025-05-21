
from datetime import datetime
from utils.alert import send_alert

SCHEDULE_TIMES = {"00:00", "06:00", "12:00", "18:00"}
last_sent_minute = {}

def fmt(val, prefix="$", digits=2):
    try:
        return f"{prefix}{float(val):,.{digits}f}"
    except:
        return "N/A"

def pct(n, d):
    return f"{(n / d * 100):.2f}%" if d > 0 else "N/A"

async def margin_full_snapshot(context, params):
    if not params.get("enabled", True):
        return

    now = datetime.utcfromtimestamp(context["now"])
    now_str = now.strftime("%H:%M")
    minute_key = now.strftime("%Y-%m-%d %H:%M")

    if now_str not in SCHEDULE_TIMES:
        return

    accounts = params.get("account")
    if isinstance(accounts, str):
        accounts = [accounts]

    for account_id in accounts:
        if last_sent_minute.get(account_id) == minute_key:
            continue
        last_sent_minute[account_id] = minute_key

        data = context["accounts"].get(account_id)
        if not data:
            continue

        lines = []

        # --- sum report  ---
        wallet = float(data.get("maintotalWalletBalance", 0))
        initial = float(data.get("maintotalInitialMargin", 0))
        maint = float(data.get("maintotalMaintMargin", 0))
        pos_init = float(data.get("maintotalPositionInitialMargin", 0))
        withdraw = float(data.get("mainmaxWithdrawAmount", 0))

        lines.append(f"*Maintenance Margin Overview - {account_id}*")
        lines.append("```")
        lines.append(f"{'Metric':<35} {'Value':>20}")
        lines.append("-" * 55)
        lines.append(f"{'Wallet Balance':<35} {fmt(wallet):>20}")
        lines.append(f"{'Initial Margin':<35} {fmt(initial):>20}  ({pct(initial, wallet)})")
        lines.append(f"{'Maintenance Margin':<35} {fmt(maint):>20}  ({pct(maint, wallet)})")
        lines.append(f"{'Position Initial Margin':<35} {fmt(pos_init):>20}  ({pct(pos_init, wallet)})")
        lines.append(f"{'Max Withdrawable':<35} {fmt(withdraw):>20}  ({pct(withdraw, wallet)})")
        lines.append("```")

        # --- coin  ---
        symbols = set()
        for k in data:
            if "-" in k and k.endswith("initialMargin"):
                symbols.add(k.replace("initialMargin", ""))

        if symbols:
            lines.append("*Pair Margin Summary*")
            lines.append("```")
            lines.append(f"{'Pair':<15} {'InitMargin':>14} {'MaintMargin':>14} {'UnPnl':>10}")
            lines.append("-" * 55)
            for sym in sorted(symbols):
                i = fmt(data.get(f"{sym}initialMargin", 0))
                m = fmt(data.get(f"{sym}maintMargin", 0))
                u = fmt(data.get(f"{sym}crossUnPnl", 0))
                lines.append(f"{sym:<15} {i:>14} {m:>14} {u:>10}")
            lines.append("```")

        # --- coin report  ---
        for asset in ["USDT", "USDC", "BTC"]:
            found = any(f"{asset}{k}" in data for k in ["walletBalance", "initialMargin", "marginBalance"])
            if not found:
                continue
            lines.append(f"*{asset} Breakdown*")
            lines.append("```")
            for key in [
                "walletBalance",
                "initialMargin",
                "maintMargin",
                "unrealizedProfit",
                "marginBalance",
                "positionInitialMargin",
                "openOrderInitialMargin",
                "availableBalance",
                "maxWithdrawAmount"
            ]:
                val = data.get(f"{asset}{key}")
                lines.append(f"{key:<30} {fmt(val):>20}")
            lines.append("```")

        # --- USDT vs USDC Ratio  ---
        usdt_balance = float(data.get("USDTwalletBalance", 0))
        usdc_balance = float(data.get("USDCwalletBalance", 0))
        total = usdt_balance + usdc_balance

        if total > 0:
            usdt_ratio = usdt_balance / total
            usdc_ratio = 1 - usdt_ratio
            lines.append("*USDT vs USDC Ratio*")
            lines.append("```")
            lines.append(f"USDT: {usdt_ratio * 100:.2f}%")
            lines.append(f"USDC: {usdc_ratio * 100:.2f}%")
            lines.append("```")
        else:
            lines.append("*USDT vs USDC Ratio*")
            lines.append("```")
            lines.append("No USDT/USDC balance available.")
            lines.append("```")

        send_alert("\n".join(lines))
