#!/bin/bash
# UserPromptSubmit hook: asks passageway whether the sources know something about this prompt and, if so, hands Claude
# the passages as additional context. It must never get in the way: no config, a slow or broken server, or any other
# failure → no output, exit 0.
set -u

# The configs, {"url", "token"} each: passageway.json and one passageway-<instance>.json per further instance, in the
# plugin's data folder or else in the folder the setup skill writes without the plugin variable; failing those, one
# written by trilium-recall, which passageway replaces (same shape).
fallback="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/plugin-data/passageway"
own="${CLAUDE_PLUGIN_DATA:-$fallback}"
set --
for dir in "$own" "$fallback"; do
  for candidate in "$dir/passageway.json" "$dir"/passageway-*.json; do
    [ -f "$candidate" ] && set -- "$@" "$candidate"
  done
  [ $# -gt 0 ] && break
done
if [ $# -eq 0 ]; then
  for candidate in "$(dirname "$own")"/trilium-recall*/recall.json "$(dirname "$fallback")"/trilium-recall*/recall.json \
      "$(dirname "$own")"/trilium-llm-wiki*/recall.json "$(dirname "$fallback")"/trilium-llm-wiki*/recall.json; do
    [ -f "$candidate" ] && { set -- "$candidate"; break; }
  done
fi
# Always drain stdin: exiting with a large prompt unread leaves the writer a broken pipe.
{ [ $# -gt 0 ] && command -v python3 >/dev/null && command -v curl >/dev/null; } || { cat >/dev/null; exit 0; }

umask 077
work=$(mktemp -d 2>/dev/null) || { cat >/dev/null; exit 0; }
trap 'rm -rf "$work"' EXIT
cat >"$work/input"

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
parts = []
for path in sys.argv[1:]:
    try:
        parts.append(json.load(open(path)).get("context") or "")
    except Exception:
        pass
context = "\n\n".join(p for p in parts if p)
if context:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "UserPromptSubmit", "additionalContext": context}}))
PY

# One request per instance, all at once, so several instances still answer within the one time limit.
i=0
for config in "$@"; do
  i=$((i + 1))
  mkdir "$work/$i"
  python3 -I "$work/request.py" "$config" "$work/$i" <"$work/input" 2>/dev/null || continue
  curl -sS --fail --max-time 1.5 -K "$work/$i/curlrc" -H 'Content-Type: application/json' \
    --data-binary "@$work/$i/body.json" "$(cat "$work/$i/url")" -o "$work/$i/response" 2>/dev/null &
done
wait

set --
j=1
while [ $j -le $i ]; do
  [ -f "$work/$j/response" ] && set -- "$@" "$work/$j/response"
  j=$((j + 1))
done
[ $# -gt 0 ] && python3 -I "$work/reply.py" "$@" 2>/dev/null
exit 0
