#!/bin/bash
# UserPromptSubmit hook: asks passageway whether the sources know something about this prompt and, if so, hands Claude
# the passages as additional context. It must never get in the way: no config, a slow or broken server, or any other
# failure → no output, exit 0.
set -u

# The config, {"url", "token"}: the plugin's data folder, the folder the setup skill writes without the plugin variable,
# or one written by trilium-recall, which passageway replaces (same shape).
fallback="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway"
own="${CLAUDE_PLUGIN_DATA:-$fallback}"
config=""
for candidate in "$own/passageway.json" "$fallback/passageway.json" \
    "$(dirname "$own")"/trilium-recall*/recall.json "$(dirname "$fallback")"/trilium-recall*/recall.json \
    "$(dirname "$own")"/trilium-llm-wiki*/recall.json "$(dirname "$fallback")"/trilium-llm-wiki*/recall.json; do
  [ -f "$candidate" ] && { config="$candidate"; break; }
done
# Always drain stdin: exiting with a large prompt unread leaves the writer a broken pipe.
{ [ -n "$config" ] && command -v python3 >/dev/null && command -v curl >/dev/null; } || { cat >/dev/null; exit 0; }

umask 077
work=$(mktemp -d 2>/dev/null) || { cat >/dev/null; exit 0; }
trap 'rm -rf "$work"' EXIT

# The python goes through files in the work folder so that stdin stays the hook input (a pasted log can exceed the argv
# limit). One call reads it and the config and writes the request body to a file only this user can read; the server
# embeds only the start of a prompt, so 20000 characters are plenty. Neither the token nor the prompt ever goes on a
# command line.
cat >"$work/request.py" <<'PY'
import json, sys
raw = sys.stdin.read()
try:
    hook = json.loads(raw)
    cfg = json.load(open(sys.argv[1]))
    url, token = cfg["url"].rstrip("/"), cfg["token"]
    body = {"prompt": (hook.get("prompt") or "")[:20000], "session_id": hook.get("session_id"), "cwd": hook.get("cwd")}
    if "\n" in url or "\n" in token:
        raise ValueError("bad config")
except Exception:
    sys.exit(1)
work = sys.argv[2]
open(work + "/url", "w").write(url + "/recall")
# the token goes in through a curl config: curl's config parser treats \ and " specially inside the quotes
quoted = token.replace("\\", "\\\\").replace('"', '\\"')
open(work + "/curlrc", "w").write('header = "Authorization: Bearer ' + quoted + '"\n')
open(work + "/body.json", "w").write(json.dumps(body))
PY
cat >"$work/reply.py" <<'PY'
import json, sys
try:
    context = json.load(open(sys.argv[1])).get("context") or ""
except Exception:
    sys.exit(0)
if context:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}}))
PY

python3 -I "$work/request.py" "$config" "$work" 2>/dev/null || exit 0

curl -sS --fail --max-time 1.5 -K "$work/curlrc" -H 'Content-Type: application/json' \
  --data-binary "@$work/body.json" "$(cat "$work/url")" -o "$work/response" 2>/dev/null || exit 0

python3 -I "$work/reply.py" "$work/response" 2>/dev/null
exit 0
