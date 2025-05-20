import json
import time
import importlib

# Load config
with open("config/features.json") as f:
    RAW_CONFIG = json.load(f)

FEATURE_HANDLERS = {}

for name, conf in RAW_CONFIG.items():
    if conf.get("expand_by") == "account":
        for acc in conf["accounts"]:
            suffix = acc[-4:]
            inst_name = f"{name}:{suffix}"
            params = conf["params_template"].copy()
            params["account"] = acc
            module = importlib.import_module(conf["module"])
            func = getattr(module, conf["function"])
            FEATURE_HANDLERS[inst_name] = {
                "func": func,
                "params": params
            }
    else:
        module = importlib.import_module(conf["module"])
        func = getattr(module, conf["function"])
        FEATURE_HANDLERS[name] = {
            "func": func,
            "params": conf["params"]
        }

async def dispatch_to_features(pos_dict):
    context = {
        "accounts": pos_dict,
        "now": time.time()
    }
    for name, handler in FEATURE_HANDLERS.items():
        try:
            await handler["func"](context, handler["params"])
        except Exception as e:
            print(f"Error in {name}: {e}")
