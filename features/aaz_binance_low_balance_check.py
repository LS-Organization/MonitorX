import time
from utils.alert import send_alert

# Stores the last alert time per (account, coin) to enforce cooldown
last_alert_time = {}

async def aaz_binance_low_balance_check(context, params):
    thresholds = params.get("thresholds", {})
    accounts_to_check = params.get("accounts", [])
    cooldown_seconds = params.get("cooldown", 60)

    now = context["now"]
    all_positions = context["accounts"]

    for account_id in accounts_to_check:
        pos = all_positions.get(account_id)
        if not pos:
            continue

        usdt_balance = float(pos.get("USDTwalletBalance", 0))
        usdc_balance = float(pos.get("USDCwalletBalance", 0))
        bnb_balance = float(pos.get("BNBwalletBalance", 0))

        messages = []

        # Helper to check threshold & cooldown
        def should_alert(coin, balance, threshold):
            key = (account_id, coin)
            if 0 < balance < threshold:
                last_sent = last_alert_time.get(key, 0)
                if now - last_sent >= cooldown_seconds:
                    last_alert_time[key] = now
                    return True
            return False

        if should_alert("USDT", usdt_balance, thresholds.get("USDT", 0)):
            messages.append(f"• [{account_id}] USDT balance is low: ${usdt_balance:,.2f} < ${thresholds.get('USDT', 0):,}")

        if should_alert("USDC", usdc_balance, thresholds.get("USDC", 0)):
            messages.append(f"• [{account_id}] USDC balance is low: ${usdc_balance:,.2f} < ${thresholds.get('USDC', 0):,}")

        if should_alert("BNB", bnb_balance, thresholds.get("BNB", 0)):
            messages.append(f"• [{account_id}] BNB balance is low: {bnb_balance:,.4f} < {thresholds.get('BNB', 0)}")

        if messages:
            msg = f"""
*Low Balance Alert*

{chr(10).join(messages)}
"""
            send_alert(msg)
