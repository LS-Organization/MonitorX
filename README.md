# Real-Time Multi-Account Monitoring System

This is a modular, real-time monitoring framework designed for tracking and alerting on multiple trading accounts across exchanges. It processes live WebSocket data and dispatches account-specific logic functions for things like delta checks, balance monitoring, risk exposure, and more.

The system is data-driven, configuration-controlled, and built to be extensible and resilient.

---

## Features

- Galio Live WebSocket ingestion 
- Dispatcher reads from JSON config to route accounts to logic
- Plugin-style logic modules (e.g. `delta_check`, `daily_report`)
- Hook-based alert system (Slack by default, easily extendable)
- Fault isolation: one failing function won’t break others
- Time-aware checks supported (e.g. daily summaries)

---

How it works (layer by layer)
1. Data Layer – What drives the system (input)
 This layer just listens to incoming data from Galio (positions, balances, etc.) via WebSocket. When data updates, everything else reacts.
Right now, we're using one WebSocket source, but it can be extended to include others—Binance, OKX, Bybit, or even REST-based feeds.
a trigger layer.


2. Dispatcher Layer – Who runs what (routing)
 This part decides what logic should run for which account. It reads from a config file (account_features.json) where we map each account to its assigned checks.
For example:
Some accounts might check for the USDT balance level and delta mismatches
Others might only check risk exposure
The dispatcher just routes—it doesn't care how the functions work.
We could expand this later to support things like conditional checks or execution order control.

3. Logic Layer – What actually gets checked (functions)
These are individual Python functions. Each one does one job: check balance, check position delta, check token exposure, etc.
They take the account name and balance data as input, and they can optionally raise an alert using a shared alert hook.
Each function is fully independent. They don't share a state and don't depend on each other. You can add new ones without the risk of breaking existing ones.

4. Alert Layer (over kill) – Where alerts are sent (output)
 Functions call something like send_alert(...), and the alert system decides what to do with it.
That could be sending to Slack, writing to a log file, calling a webhook, etc. More can be added later.
This keeps alert logic separate from decision logic.

Design goals are
 - Let data drive everything (no polling, no scheduling)
 - Let config define behavior (not hardcoded)but i will do hardcoded function first
 - Keep functions small, focused, and independent
 - Make alerts reusable and easy to reroute
 - Be able to change one layer without touching the others
 - Don't let one broken function bring down the whole system(try catch...)

Adding something new by:
 - Write a new function → plug it in( Logic Layer )
 - Update account config → change behavior(Dispatcher Layer)
 - Add an alert channel → no need to change logic( Alert Layer)
 - It's meant to be flexible enough that these changes can be done quickly and safely.
below is the workflow chart

![image_720](https://github.com/user-attachments/assets/bab881fd-20d1-4e3e-8906-e2d7b0dc5e78)



## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/LS-Organization/MonitorX.git
cd MonitorX

2.Create and activate a virtual environment
python -m venv venv
source venv/bin/activate 

3.Install dependencies
pip install -r requirements.txt

4. Create .env file
example 
USERNAME=your_username
PASSWORD=your_password
WS_URI=
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

