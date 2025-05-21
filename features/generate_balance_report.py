from datetime import datetime
from utils.alert import send_alert

# Official report times in UTC
SCHEDULE_TIMES = ["00:00", "06:00", "12:00", "18:00"]
#SCHEDULE_TIMES = ["13:19"]

# Stores the last sent minute to avoid duplicate reports
last_sent_minute = None

def format_usd(value):
    return f"${value:,.2f}"

async def generate_balance_report(context, params):
    global last_sent_minute

    now_utc = datetime.utcfromtimestamp(context["now"])
    current_time_str = now_utc.strftime("%H:%M")


    if current_time_str not in SCHEDULE_TIMES:
        last_sent_minute = None  
        return

    if last_sent_minute == current_time_str:
        return

    last_sent_minute = current_time_str

    accounts = params.get("accounts", [])
    all_pos = context["accounts"]

    total_usdt = 0
    total_usdc = 0
    total_bnb = 0
    total_combined = 0

    lines = ["*Binance Balance Report (Scheduled)*", f"_Time: {current_time_str} UTC_", ""]

    for account_id in accounts:
        pos = all_pos.get(account_id)
        if not pos:
            continue

        usdt = float(pos.get("USDTwalletBalance", 0))
        usdc = float(pos.get("USDCwalletBalance", 0))
        bnb = float(pos.get("BNBwalletBalance", 0))
        total = float(pos.get("maintotalWalletBalance", 0))

        total_usdt += usdt
        total_usdc += usdc
        total_bnb += bnb
        total_combined += total

        usdt_pct = (usdt / total * 100) if total else 0
        usdc_pct = (usdc / total * 100) if total else 0

        lines.append(
            f"*{account_id}*\n"
            f"• USDT: {format_usd(usdt)} ({usdt_pct:.1f}%)\n"
            f"• USDC: {format_usd(usdc)} ({usdc_pct:.1f}%)\n"
            f"• BNB:  {bnb:,.4f}\n"
            f"• TOTAL: {format_usd(total)}\n"
        )

    lines.append("-----------------------")
    lines.append("*Summary Totals*")
    lines.append(f"• USDT: {format_usd(total_usdt)}")
    lines.append(f"• USDC: {format_usd(total_usdc)}")
    lines.append(f"• BNB:  {total_bnb:,.4f}")
    lines.append(f"• TOTAL: {format_usd(total_combined)}")

    send_alert("\n".join(lines))
