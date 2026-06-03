# Evals — Simplified for AI

Internal QA for the plugin: how we validate the skills + connector before and after
release. Not required to *use* the plugin — kept in the repo for transparency and
contributors. Safe to ignore if you're just installing the skills.

## Files
- [openai-test-cases.md](openai-test-cases.md) — the 6 cases in OpenAI's submission
  format (Scenario / User prompt / Tool triggered / Expected output). Paste into the form.
- [cases.md](cases.md) — canonical definitions: expected tool sequence, argument
  contract, and assertions for each case (agent layer + I/O layer).
- [run_evals.py](run_evals.py) — runnable harness that checks the **I/O layer**
  (the tools behave as the skills claim) against the live API.
- [results.md](results.md) — golden outputs captured from live runs + pass/fail log.

## What the two layers mean
- **Agent layer** — does the model call the right tool(s) for the prompt? This is
  what OpenAI's reviewers exercise in Codex. We eyeball it against the pass criteria
  in `cases.md`.
- **I/O layer** — do the tools return what the skills promise? `run_evals.py`
  automates this deterministically (no model in the loop).

## Prerequisites
- An OAuth access token (`SMP_ACCESS_TOKEN`). Tokens last ~1 hour.
- AI credits (only for image cases, run with `--with-image`).
- A connected social account in the workspace (only for the analytics case; the
  draft cases use accountless drafts and need no connected account).

## Minting an access token (DCR + PKCE)

The static OAuth apps aren't loaded on prod, so register a client dynamically:

```bash
# 1. Register a public client (RFC 7591 DCR) — returns a client_id
curl -s -X POST "https://api.simplified.com/api/o/register/" \
  -H "Content-Type: application/json" \
  -d '{"client_name":"eval client","redirect_uris":["http://localhost:3000/oauth/callback"],"token_endpoint_auth_method":"none"}'

# 2. Build a PKCE challenge
python3 - <<'PY'
import secrets,hashlib,base64,json
v=base64.urlsafe_b64encode(secrets.token_bytes(64)).rstrip(b'=').decode()
c=base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b'=').decode()
open('/tmp/pkce.json','w').write(json.dumps({'verifier':v,'challenge':c}))
print('challenge:',c)
PY

# 3. Open the authorize URL in a browser, log in, approve. Copy `code` from the
#    redirect (http://localhost:3000/oauth/callback?code=...&state=...):
#    https://api.simplified.com/api/o/authorize/?response_type=code
#      &client_id=<CLIENT_ID>&redirect_uri=http://localhost:3000/oauth/callback
#      &scope=openid+read+write+ai:generate+social:write
#      &code_challenge=<CHALLENGE>&code_challenge_method=S256&state=x

# 4. Exchange the code for a token
VERIFIER=$(python3 -c "import json;print(json.load(open('/tmp/pkce.json'))['verifier'])")
curl -s -X POST "https://api.simplified.com/api/o/token/" \
  -d grant_type=authorization_code -d code=<CODE> \
  --data-urlencode redirect_uri=http://localhost:3000/oauth/callback \
  -d client_id=<CLIENT_ID> -d code_verifier=$VERIFIER
# → copy access_token
```

## Running

```bash
export SMP_ACCESS_TOKEN=<access_token>
python3 evals/run_evals.py              # read-only + draft cases (no credit spend)
python3 evals/run_evals.py --with-image # also image-gen + cross-skill (consume credits)
python3 evals/run_evals.py --keep-drafts
```

Exit code is non-zero if any non-skipped case fails. Image cases default to
`flux.flux-schnell` (8 credits); override with `SMP_EVAL_MODEL`.
