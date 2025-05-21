import time
from utils.alert import send_alert

# check if the alert is already sent last time 
last_alert_time = {}

def fmt(val, prefix="$", digits=2):
    try:
        return f"{prefix}{float(val):,.{digits}f}"
    except:
        return "N/A"

async def margin_risk_alert(context, params):
    now = context["now"]
    account_list = params.get("accounts", [])
    cooldown = params.get("cooldown", 60)
    thresholds = params.get("thresholds", {})

    for account in account_list:
        data = context["accounts"].get(account)
        if not data:
            continue

        wallet = float(data.get("maintotalWalletBalance", 0)) or 1
        initial = float(data.get("maintotalInitialMargin", 0))
        maint = float(data.get("maintotalMaintMargin", 0))
        pos_init = float(data.get("maintotalPositionInitialMargin", 0))
        withdraw = float(data.get("mainmaxWithdrawAmount", 0))

        usdt = float(data.get("USDTwalletBalance", 0))
        usdc = float(data.get("USDCwalletBalance", 0))
        us_ratio = (usdt / usdc) if usdc > 0 else float('inf')
        us_total = usdt + usdc
        usdt_pct = (usdt / us_total * 100) if us_total > 0 else 0
        usdc_pct = 100 - usdt_pct if us_total > 0 else 0

        ratio_initial = initial / wallet
        ratio_maint = maint / wallet
        ratio_pos = pos_init / wallet
        ratio_withdraw = withdraw / wallet

        alerts = []

        def should_alert(metric_key, message):
            key = (account, metric_key)
            last = last_alert_time.get(key, 0)
            if now - last >= cooldown:
                alerts.append(message)
                last_alert_time[key] = now

        # Check if the account is in
        if ratio_initial > thresholds.get("initial_margin", 0.8):
            should_alert("initial_margin", f" Initial Margin Ratio = {ratio_initial:.2%} > {thresholds['initial_margin']:.0%}")

        if ratio_maint > thresholds.get("maint_margin", 0.2):
            should_alert("maint_margin", f" Maint. Margin Ratio = {ratio_maint:.2%} > {thresholds['maint_margin']:.0%}")

        if ratio_pos > thresholds.get("position_margin", 0.75):
            should_alert("position_margin", f" Position Margin Ratio = {ratio_pos:.2%} > {thresholds['position_margin']:.0%}")

        min_r = thresholds.get("usdt_usdc_ratio_min", 0.5)
        max_r = thresholds.get("usdt_usdc_ratio_max", 2.5)
        if not (min_r <= us_ratio <= max_r):
            should_alert("usdt_usdc_ratio", f" USDT/USDC Ratio = {us_ratio:.2f} not in [{min_r}, {max_r}]")

        if alerts:
            def row(label, val, ratio=None):
                ratio_part = f"   ({ratio:.2%})" if ratio is not None else ""
                return f"{label:<25} {fmt(val):>14}{ratio_part}"

            msg_lines = [
                f" *[Risk Alert] {account}*",
                "",
                *alerts,
                "",
                "```",
                f"{'Metric':<25} {'Value':>14}",
                "-" * 42,
                f"{'Wallet Balance':<25} {fmt(wallet):>14}",
                row("Initial Margin", initial, ratio_initial),
                row("Maint. Margin", maint, ratio_maint),
                row("Position Init Margin", pos_init, ratio_pos),
                row("Max Withdrawable", withdraw, ratio_withdraw),
                row("USDT", usdt, usdt_pct / 100),
                row("USDC", usdc, usdc_pct / 100),
                f"{'USDT/USDC Ratio':<25} {us_ratio:>14.2f}",
                "```"
        ]

            send_alert("\n".join(msg_lines))
