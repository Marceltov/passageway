#!/bin/bash
# Self-check for recall-hook.sh against a stub server. No framework: run `bash scripts/test-recall-hook.sh`.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
hook="$script_dir/recall-hook.sh"
tmp="$(mktemp -d)"
stub_pid=""
trap '[ -n "$stub_pid" ] && kill "$stub_pid" 2>/dev/null; rm -rf "$tmp"' EXIT

export CLAUDE_PLUGIN_DATA="$tmp/plugin-data"
fail=0
input='{"session_id":"sess-1","cwd":"/root/notes","hook_event_name":"UserPromptSubmit","prompt":"why is CT 115 slow"}'

cat > "$tmp/stub.py" <<'PY'
import http.server, json, sys, time
tmp = sys.argv[1]
class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        open(f"{tmp}/last-request", "w").write(json.dumps({"path": self.path, "auth": self.headers.get("Authorization"), "body": json.loads(body)}))
        mode = open(f"{tmp}/mode").read().strip()
        if mode == "slow":
            time.sleep(5)
        status, payload = {"context": (200, json.dumps({"context": "Recall (notes) — hit"})),
                           "empty": (200, json.dumps({"context": ""})),
                           "error": (500, "boom"), "garbage": (200, "not json"),
                           "slow": (200, json.dumps({"context": "late"}))}[mode]
        self.send_response(status); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(payload.encode())
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
open(f"{tmp}/port", "w").write(str(srv.server_address[1]))
srv.serve_forever()
PY
echo context > "$tmp/mode"
python3 -I "$tmp/stub.py" "$tmp" & stub_pid=$!
for _ in $(seq 1 50); do [ -s "$tmp/port" ] && break; sleep 0.1; done
port=$(cat "$tmp/port")

same() {  # the same JSON (or both empty), whatever the escaping
  python3 -c 'import json, sys; a, b = sys.argv[1:]; sys.exit(0 if (a.strip() == b.strip() == "") or (a.strip() and b.strip() and json.loads(a) == json.loads(b)) else 1)' "$1" "$2"
}

check() {  # name, expected output, mode
  echo "$3" > "$tmp/mode"
  rm -f "$tmp/last-request"
  out=$(printf '%s' "$input" | bash "$hook")
  if same "$out" "$2"; then echo "ok   $1"; else echo "FAIL $1: got '$out'"; fail=1; fi
}

# no config at all: silent
check "no config → nothing" "" context
mkdir -p "$CLAUDE_PLUGIN_DATA" && printf '{"url": "http://127.0.0.1:%s", "token": "s3cret"}' "$port" > "$CLAUDE_PLUGIN_DATA/passageway.json"
expected='{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": "Recall (notes) — hit"}}'
check "a hit becomes additionalContext" "$expected" context
grep -q '"auth": "Bearer s3cret"' "$tmp/last-request" && grep -q '"cwd": "/root/notes"' "$tmp/last-request" && echo "ok   token in the header, cwd in the body" || { echo "FAIL request"; fail=1; }
check "no hit → nothing" "" empty
check "server error → nothing" "" error
check "garbage → nothing" "" garbage
check "slow server → nothing within the limit" "" slow
# a legacy trilium-recall config is still read
rm "$CLAUDE_PLUGIN_DATA/passageway.json"; mkdir -p "$tmp/plugin-data/../trilium-recall" 2>/dev/null; mkdir -p "$(dirname "$CLAUDE_PLUGIN_DATA")/trilium-recall"
printf '{"url": "http://127.0.0.1:%s", "token": "s3cret"}' "$port" > "$(dirname "$CLAUDE_PLUGIN_DATA")/trilium-recall/recall.json"
check "a trilium-recall config still works" "$expected" context
ps -o args= -p "$stub_pid" >/dev/null && grep -q s3cret <(ps -eo args= | grep -v grep | grep recall-hook || true) && { echo "FAIL token on a command line"; fail=1; } || echo "ok   the token is never on a command line"
exit $fail
