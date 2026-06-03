#!/usr/bin/env python3
"""I/O eval harness for the Simplified Codex Plugin.

Exercises the hosted-connector tools through the raw djapp API and asserts the
response shapes the skills depend on. This validates the *backend* half of each
test case in cases.md (the "expected output"); the agent/tool-routing half is
checked separately in Codex.

Auth: set SMP_ACCESS_TOKEN to a valid OAuth access token (see README.md for how to
mint one via DCR + PKCE). Base URL defaults to production.

Usage:
    export SMP_ACCESS_TOKEN=...          # required
    python run_evals.py                  # read-only + draft cases (no credit spend)
    python run_evals.py --with-image     # also run image-gen cases (consume credits)
    python run_evals.py --keep-drafts    # don't delete the drafts created by C4/C6

Exit code is non-zero if any run case fails.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import date

BASE = os.environ.get("SMP_BASE", "https://api.simplified.com").rstrip("/")
TOKEN = os.environ.get("SMP_ACCESS_TOKEN", "")
CHEAP_MODEL = os.environ.get("SMP_EVAL_MODEL", "flux.flux-schnell")  # 8 credits


@dataclass
class Result:
    name: str
    passed: bool
    msg: str
    skipped: bool = False


def _request(method: str, path: str, *, body: dict | None = None,
             params: dict | None = None) -> tuple[int, object]:
    url = f"{BASE}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {TOKEN}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, raw


def poll_task(task_id: str, timeout: int = 180) -> dict:
    """Poll GET /api/v1/tasks/{id} until terminal. Returns the final envelope."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, body = _request("GET", f"/api/v1/tasks/{task_id}")
        st = body.get("status") if isinstance(body, dict) else None
        if st in ("SUCCESS", "FAILURE", "REVOKED"):
            return body
        time.sleep(4)
    return {"status": "TIMEOUT"}


def _result_list(envelope: dict) -> list:
    detail = envelope.get("detail") or envelope.get("info") or {}
    return detail.get("result") or []


# --------------------------------------------------------------------------- #
# Cases
# --------------------------------------------------------------------------- #

def case_image(name: str, model: str, params: dict, storage: str) -> Result:
    status, body = _request(
        "POST", "/api/v1/ai/image/ai-generate-image-v2",
        body={"model": model, "capability": "prompt", "storage": storage,
              "parameters": params},
    )
    if status not in (200, 201, 202) or not isinstance(body, dict):
        return Result(name, False, f"generate returned {status}: {body}")
    task_id = body.get("task_id")
    if not task_id:
        return Result(name, False, f"no task_id in {body}")
    final = poll_task(task_id)
    if final.get("status") != "SUCCESS":
        return Result(name, False, f"task ended {final.get('status')}: {final}")
    results = _result_list(final)
    if not results:
        return Result(name, False, "empty result list")
    item = results[0]
    if storage == "asset":
        if not (isinstance(item, dict) and item.get("asset_id") and item.get("url")):
            return Result(name, False, f"asset mode: expected {{asset_id,url}}, got {item}")
        return Result(name, True, f"asset_id={item['asset_id']}")
    # transient → result[0] is a URL string
    if not (isinstance(item, str) and item.startswith("http")):
        return Result(name, False, f"transient mode: expected URL string, got {type(item).__name__}")
    return Result(name, True, f"url={item[:60]}…")


def case_accounts() -> tuple[Result, list]:
    status, body = _request("GET", "/api/v1/service/social-media/get-accounts")
    if status != 200 or not isinstance(body, dict):
        return Result("C3 accounts", False, f"{status}: {body}"), []
    accounts = body.get("accounts") if isinstance(body.get("accounts"), list) else body.get("results", [])
    if not accounts:
        return Result("C3 accounts", True, "0 connected (valid empty state)", skipped=False), []
    a = accounts[0]
    ok = all(k in a for k in ("id", "name", "type"))
    return Result("C3 accounts", ok, f"{len(accounts)} accounts; first id={a.get('id')} type={a.get('type')}"), accounts


def case_analytics(accounts: list) -> Result:
    if not accounts:
        return Result("C5 analytics", False, "no connected account to query", skipped=True)
    acct = accounts[0]["id"]
    today = date.today()
    first_this = today.replace(day=1)
    # previous calendar month
    if first_this.month == 1:
        date_from = date(first_this.year - 1, 12, 1)
    else:
        date_from = date(first_this.year, first_this.month - 1, 1)
    date_to = min(first_this, today)  # start of this month, never future
    status, body = _request(
        "GET", "/api/v1/service/social-media/analytics/aggregated",
        params={"account_id": acct, "date_from": date_from.isoformat(),
                "date_to": date_to.isoformat()},
    )
    if status != 200 or not isinstance(body, dict):
        return Result("C5 analytics", False, f"{status}: {body}")
    baseline = body.get("baseLine") or {}
    expected = {"impressions_aggregated", "engagement_aggregated",
                "followers_aggregated", "publishing_aggregated"}
    missing = expected - set(baseline)
    if missing:
        return Result("C5 analytics", False, f"baseLine missing KPIs: {missing}")
    return Result("C5 analytics", True, f"acct={acct} KPIs present")


def case_draft(keep: bool, media: list | None = None, tag: str = "C4 draft") -> Result:
    msg = "Eval draft — announcing our new AI image feature. (safe to delete)"
    body = {"message": msg, "action": "draft"}
    if media:
        body["media"] = media
        body["additional"] = {"instagram": {"postType": {"value": "post"},
                                            "channel": {"value": "direct"}}}
    status, resp = _request("POST", "/api/v1/service/social-media/create", body=body)
    if status not in (200, 201) or not isinstance(resp, dict):
        return Result(tag, False, f"create returned {status}: {resp}")
    # best-effort cleanup
    if not keep:
        ids = []
        for key in ("id", "group_id", "draft_id"):
            if resp.get(key):
                ids.append(str(resp[key]))
        try:
            if ids:
                _request("POST", "/api/v1/service/social-media/delete-draft",
                         body={"draft_ids": ids})
        except Exception:
            pass  # cleanup is best-effort; never fail the case on it
    return Result(tag, True, f"draft created (action=draft); cleanup={'kept' if keep else 'attempted'}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--with-image", action="store_true", help="run image-gen cases (consume credits)")
    ap.add_argument("--keep-drafts", action="store_true", help="don't delete created drafts")
    args = ap.parse_args()

    if not TOKEN:
        print("ERROR: set SMP_ACCESS_TOKEN (see README.md to mint one).", file=sys.stderr)
        return 2

    results: list[Result] = []

    if args.with_image:
        results.append(case_image("C1 image (transient)", CHEAP_MODEL,
                                   {"prompt": "a white ceramic coffee cup on a white background",
                                    "aspect_ratio": "1:1", "count": 1}, "transient"))
        results.append(case_image("C2 image (16:9 text)", "ideogram.ideogram-v3-turbo",
                                   {"prompt": 'a promo banner that says "Summer Sale" in bold modern type',
                                    "aspect_ratio": "16:9"}, "transient"))
    else:
        results.append(Result("C1/C2 image", False, "skipped (pass --with-image to run; consumes credits)", skipped=True))

    acct_result, accounts = case_accounts()
    results.append(acct_result)
    results.append(case_analytics(accounts))
    results.append(case_draft(args.keep_drafts))

    # C6 cross-skill: generate an asset, then draft a post that references it
    if args.with_image:
        img = case_image("C6 image (asset)", CHEAP_MODEL,
                         {"prompt": "a product photo of a sneaker on white",
                          "aspect_ratio": "1:1", "count": 1}, "asset")
        results.append(img)
        if img.passed:
            asset_id = img.msg.split("asset_id=")[-1]
            results.append(case_draft(args.keep_drafts, media=[asset_id], tag="C6 draft+media"))
        else:
            results.append(Result("C6 draft+media", False, "skipped (asset gen failed)", skipped=True))
    else:
        results.append(Result("C6 cross-skill", False, "skipped (needs --with-image)", skipped=True))

    print(f"\nSimplified Codex Plugin — eval run @ {BASE}\n" + "-" * 60)
    failed = 0
    for r in results:
        if r.skipped:
            tag = "SKIP"
        elif r.passed:
            tag = "PASS"
        else:
            tag = "FAIL"
            failed += 1
        print(f"[{tag}] {r.name:24} {r.msg}")
    print("-" * 60)
    print(f"{sum(1 for r in results if r.passed and not r.skipped)} passed, "
          f"{failed} failed, {sum(1 for r in results if r.skipped)} skipped")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
