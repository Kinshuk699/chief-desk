#!/usr/bin/env python3
"""calibrate.py: score jev_check.py's questions against the known-answer sets.

    python3 calibrate.py [--runs 2] [--model jev-1.14.0] [--json results.json]

Claims: 20 claim/passage pairs labelled supports / contradicts / says_nothing.
Prose:  12 paragraphs labelled per tell (1 present, 0 absent, null ambiguous: excluded).
Reports accuracy, the confidence of every wrong answer (the auto-accept threshold must sit
above them), run-to-run stability, per-tell precision/recall at the current thresholds,
and the separating range for each threshold. Cost is a fraction of a cent per run.
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jev_check as jc  # noqa: E402


def load(name):
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def claims_report(rows, runs, key, model):
    by_run = [jc.run_claims([{k: r[k] for k in ("id", "claim", "passage", "source") if k in r} for r in rows], key, model, 4, False)
              for _ in range(runs)]
    label = {r["id"]: r["label"] for r in rows}
    to_choice = {"SUPPORTED": "supports", "CONTRADICTED": "contradicts", "NOT_SUPPORTED": "says_nothing"}
    print("\n## Claims (choice: supports / contradicts / says_nothing)\n")
    print("| id | label | run1 | conf1 | " + " | ".join(f"run{k+1}" for k in range(1, runs)) + " | case |")
    print("|---|---|---|---|" + "---|" * (runs - 1) + "---|")
    case = {r["id"]: r.get("case", "") for r in rows}
    for i, res in enumerate(by_run[0]):
        rid = res["id"]
        extra = " | ".join(f"{to_choice.get(by_run[k][i].get('verdict'), by_run[k][i].get('verdict'))} "
                           f"({by_run[k][i].get('confidence')})" for k in range(1, runs))
        got = to_choice.get(res.get("verdict"), res.get("verdict"))
        mark = "" if got == label[rid] else " ✗"
        print(f"| {rid} | {label[rid]} | {got}{mark} | {res.get('confidence')} | {extra} | {case[rid]} |")
    first = by_run[0]
    right = [r for r in first if to_choice.get(r.get("verdict")) == label[r["id"]]]
    wrong = [r for r in first if to_choice.get(r.get("verdict")) != label[r["id"]]]
    print(f"\nAccuracy (run 1, argmax): {len(right)}/{len(first)}")
    for cls in ("supports", "contradicts", "says_nothing"):
        n = [r for r in first if label[r["id"]] == cls]
        ok = [r for r in n if to_choice.get(r.get("verdict")) == cls]
        print(f"  {cls}: {len(ok)}/{len(n)}")
    false_support = [r for r in first if r.get("verdict") == "SUPPORTED" and label[r["id"]] != "supports"]
    print(f"False SUPPORTED (the expensive error): {len(false_support)} -> "
          f"{[(r['id'], r['confidence']) for r in false_support]}")
    print(f"Wrong answers' confidence: {sorted((r['confidence'], r['id']) for r in wrong)}")
    print(f"Right answers' confidence: min {min(r['confidence'] for r in right) if right else '-'}")
    for t in (0.6, 0.7, 0.8, 0.9, 0.95):
        auto = [r for r in first if r["confidence"] >= t]
        auto_wrong = [r for r in auto if to_choice.get(r.get("verdict")) != label[r["id"]]]
        print(f"  AUTO >= {t}: {len(auto)}/{len(first)} auto, {len(auto_wrong)} auto-wrong, "
              f"{len(first) - len(auto)} to review")
    if runs > 1:
        flips = sum(1 for i in range(len(first)) if len({by_run[k][i].get("verdict") for k in range(runs)}) > 1)
        drift = max(abs(by_run[k][i]["confidence"] - first[i]["confidence"])
                    for k in range(1, runs) for i in range(len(first)))
        print(f"Stability over {runs} runs: {flips} verdict flips, max confidence drift {drift:.3f}")
    return by_run


def prose_report(rows, runs, key, model):
    by_run = [jc.run_prose([{"id": r["id"], "text": r["text"]} for r in rows], key, model, 4, False)
              for _ in range(runs)]
    first = by_run[0]
    lab = {r["id"]: r["label"] for r in rows}
    tells = list(jc.PROSE_NOULS)
    print("\n## Prose (noul p(yes) per tell; generic score 0..3)\n")
    print("| id | " + " | ".join(tells) + " | generic | code checks |")
    print("|---|" + "---|" * len(tells) + "---|---|")
    for r in first:
        cells = []
        for t in tells:
            want = lab[r["id"]][t]
            p = r["nouls"][t]
            tag = "" if want is None else ("●" if want == 1 else "○")
            cells.append(f"{p:.2f}{tag}")
        g = lab[r["id"]]["generic"]
        cc = f"em={r['em_dashes']} vocab={len(r['ai_vocab'])} stacc={len(r['staccato'])}"
        print(f"| {r['id']} | " + " | ".join(cells) + f" | {r['generic']:.2f} ({g}) | {cc} |")
    print("\n● = labelled present, ○ = labelled absent, no mark = ambiguous (excluded)")
    for t in tells + ["generic"]:
        pos, neg = [], []
        for r in first:
            want = lab[r["id"]][t]
            if want is None:
                continue
            val = r["generic"] if t == "generic" else r["nouls"][t]
            (pos if want in (1, "high") else neg).append(val)
        thr = jc.GENERIC_FLAG if t == "generic" else jc.NOUL_FLAG[t]
        tp = sum(v >= thr for v in pos)
        fp = sum(v >= thr for v in neg)
        sep = (f"separable: any threshold in ({max(neg):.2f}, {min(pos):.2f}]"
               if pos and neg and min(pos) > max(neg) else
               f"NOT separable: min present {min(pos) if pos else '-'}, max absent {max(neg) if neg else '-'}")
        print(f"  {t}: at {thr}: recall {tp}/{len(pos)}, false flags {fp}/{len(neg)}; {sep}")
    if runs > 1:
        drift = max(abs(by_run[k][i]["nouls"][t] - first[i]["nouls"][t])
                    for k in range(1, runs) for i in range(len(first)) for t in tells)
        print(f"Stability over {runs} runs: max noul drift {drift:.3f}")
    return by_run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=2)
    ap.add_argument("--model", default=jc.MODEL)
    ap.add_argument("--json", help="save raw results here")
    args = ap.parse_args()
    key = jc.load_key()
    c = claims_report(load("calib_claims.jsonl"), args.runs, key, args.model)
    p = prose_report(load("calib_prose.jsonl"), args.runs, key, args.model)
    cost = jc.USAGE.input_tokens / 1e6 * jc.PRICE_PER_M_INPUT
    print(f"\n{jc.USAGE.calls} Jev calls, {jc.USAGE.input_tokens} input tokens, ~${cost:.5f}, model {args.model}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"claims": c, "prose": p}, fh, indent=1)


if __name__ == "__main__":
    main()
