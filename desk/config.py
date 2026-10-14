import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load(path=None):
    with open(path or os.path.join(ROOT, "config.json")) as f:
        return json.load(f)
