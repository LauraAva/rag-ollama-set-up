from __future__ import annotations
import json, argparse, os
from pathlib import Path
import psycopg

# allow importing ask_rag from repo root
import sys
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import subprocess


def run_one(question: str, collection: str) -> dict:
    # Call ask_rag.py in JSON mode so we reuse identical behavior
    cmd = [
        "py",
        str(REPO_ROOT / "scripts" / "ask_rag.py"),
        question,
        "--collection",
        collection,
        "--json",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {"error": p.stderr.strip() or "ask_rag_failed", "raw": p.stdout.strip()}
    return json.loads(p.stdout)


def check_expected(result: dict, expected: dict) -> tuple[bool, dict]:
    details = {}

    if expected.get("expect_refusal"):
        # refusal means: used_rag false AND answer indicates insufficient info / denied
        ans = (result.get("answer") or "").lower()
        used = bool(result.get("used_rag"))
        ok = (not used) and ("enough information" in ans or "access denied" in ans or "don't have" in ans or "do not have" in ans)
        details["refusal_check"] = {"used_rag": used, "answer": result.get("answer")}
        return ok, details

    # expected_contains
    contains = expected.get("expected_contains") or []
    ans = (result.get("answer") or "").lower()
    contains_ok = all(s.lower() in ans for s in contains)
    details["contains_ok"] = contains_ok
    details["missing"] = [s for s in contains if s.lower() not in ans]

    # should_use_rag
    if "should_use_rag" in expected:
        details["used_rag"] = result.get("used_rag")
        if bool(result.get("used_rag")) != bool(expected["should_use_rag"]):
            return False, details

    # min audit score
    if "min_audit_score" in expected:
        score = (result.get("audit") or {}).get("score")
        details["audit_score"] = score
        if score is None or float(score) < float(expected["min_audit_score"]):
            return False, details

    return contains_ok, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default=str(REPO_ROOT / "tests" / "testcases.jsonl"))
    ap.add_argument("--run-name", default="run")
    args = ap.parse_args()

    # store run row
    with psycopg.connect("") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rag_test_runs (run_name, settings) VALUES (%s, %s) RETURNING id",
                (args.run_name, json.dumps({"file": args.file, "default_collection": os.getenv("DEFAULT_COLLECTION")}, ensure_ascii=False)),
            )
            run_id = int(cur.fetchone()[0])
        conn.commit()

    passed = 0
    total = 0

    with open(args.file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            t = json.loads(line)
            test_id = t["id"]
            collection = t.get("collection") or os.getenv("DEFAULT_COLLECTION", "public")
            question = t["question"]

            result = run_one(question, collection)
            ok, details = check_expected(result, t)

            total += 1
            passed += 1 if ok else 0

            # write result to DB
            with psycopg.connect("") as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO rag_test_results
                          (run_id, test_id, collection, question, expected, answer, used_rag, relevance_distance, audit_verdict, audit_score, passed, details)
                        VALUES
                          (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            run_id,
                            test_id,
                            collection,
                            question,
                            json.dumps(t, ensure_ascii=False),
                            result.get("answer"),
                            result.get("used_rag"),
                            result.get("relevance_distance"),
                            (result.get("audit") or {}).get("verdict"),
                            (result.get("audit") or {}).get("score"),
                            ok,
                            json.dumps({"details": details, "result": result}, ensure_ascii=False),
                        ),
                    )
                conn.commit()

            status = "PASS" if ok else "FAIL"
            print(f"[{status}] {test_id} :: {question}")

    print(f"\nDone. Passed {passed}/{total}. Results stored in rag_test_runs.id={run_id}")


if __name__ == "__main__":
    main()