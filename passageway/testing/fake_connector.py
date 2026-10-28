"""A connector over a JSON file, for tests and docs. Run: python -m passageway.testing.fake_connector <mode>."""

import json
import os
import sys


def main(argv: list[str]) -> int:
    mode = argv[1]
    if os.environ.get("FAKE_FAIL") == mode:
        print("fake failure", file=sys.stderr)
        return 1
    with open(os.environ["FAKE_ITEMS"]) as f:
        items = json.load(f)
    if mode == "check":
        print(json.dumps({"ok": True, "count": len(items), "protocol": os.environ.get("FAKE_PROTOCOL", "1")}))
    elif mode == "list":
        for item in items:
            print(json.dumps({"id": item["id"], "version": item["version"]}))
    elif mode == "fetch":
        wanted = {json.loads(line)["id"] for line in sys.stdin if line.strip()}
        for item in items:
            if item["id"] in wanted:
                print(json.dumps(item))
    elif mode == "changed":
        since = argv[3]
        for item in items:
            if item.get("updated", "") >= since:
                print(json.dumps(item))
    else:
        print(f"unknown mode {mode}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
