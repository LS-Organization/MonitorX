import json
from features.delta_check import delta_check

with open("config/account_features.json") as f:
    ACCOUNT_FEATURES = json.load(f)

FEATURE_HANDLERS = {
    "delta_check": delta_check,
}

async def dispatch_to_features(pos_dict):
    for account, balance in pos_dict.items():
        features = ACCOUNT_FEATURES.get(account, [])
        for feature in features:
            handler = FEATURE_HANDLERS.get(feature)
            if handler:
                try:
                    await handler(account, balance)
                except Exception as e:
                    print(f"[{account}] Error in {feature}: {e}")
