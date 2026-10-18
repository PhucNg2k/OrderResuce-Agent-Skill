"""Terminal demo: plays the scripted steps of each case and prints the decision cards.

    python -m runtime.cli demo              # all five cases, REPLAY mode
    python -m runtime.cli demo CASE-03      # one case
    python -m runtime.cli demo --mode LIVE_AI
"""
from __future__ import annotations

import argparse
import json

from runtime.simulator import FIXTURES, Simulator


def print_decision(d) -> None:
    print(f"  [{d.decided_at.strftime('%H:%M')}] {d.status} → {d.action}   (trigger: {d.trigger})")
    for line in d.message_vi.splitlines():
        print(f"      {line}")
    print(f"      {' · '.join(d.labels)}")


def play(sim: Simulator, case_id: str) -> None:
    expected = json.loads((FIXTURES / "expected" / f"{case_id.lower()}.json").read_text(encoding="utf-8"))
    for script in expected["scripts"]:
        print(f"\n=== {case_id} · {script['name']}")
        run, decision = sim.start(case_id)
        print_decision(decision)
        for step in script["steps"]:
            if "apply" in step:
                decisions = [sim.apply_event(run.run_id, step["apply"])]
            elif "advance_minutes" in step:
                decisions = sim.advance(run.run_id, step["advance_minutes"])
            else:
                continue
            if not decisions:
                print(f"  (+{step.get('advance_minutes')} phút: chưa có quyết định mới, vẫn đang chờ trả lời)")
            for d in filter(None, decisions):
                print_decision(d)
        print(f"  Nhật ký: runs/{run.run_id}/decisions.jsonl")


def main() -> None:
    parser = argparse.ArgumentParser(prog="order-rescue")
    sub = parser.add_subparsers(dest="cmd", required=True)
    demo = sub.add_parser("demo")
    demo.add_argument("case_id", nargs="?")
    demo.add_argument("--mode", choices=["REPLAY", "LIVE_AI"], default="REPLAY")
    args = parser.parse_args()

    sim = Simulator(mode=args.mode)
    case_ids = [args.case_id] if args.case_id else [c["case_id"] for c in sim.list_cases()]
    for case_id in case_ids:
        play(sim, case_id)


if __name__ == "__main__":
    main()
