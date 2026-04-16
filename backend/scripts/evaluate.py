import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.booking_session import clear_sessions
from app.services.chat import answer
from app.services.vector_store import ensure_seeded


def load_cases(path: Path) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def seed_faq() -> None:
    faq_path = Path(__file__).resolve().parents[1] / "app" / "data" / "faq.json"
    items = json.loads(faq_path.read_text(encoding="utf-8"))
    ensure_seeded(items)


def run_eval(cases: list[dict]) -> tuple[dict, list[dict]]:
    counts = Counter()
    details: list[dict] = []

    for case in cases:
        clear_sessions()
        result = answer(case["message"], None)
        predicted = result.get("intent", "unknown")
        expected = case["expected_intent"]
        expected_any = case.get("expected_any", [])
        accepted = [expected] + [x for x in expected_any if x != expected]
        ok = predicted in accepted

        counts["total"] += 1
        counts["correct"] += int(ok)
        counts[f"expected::{expected}"] += 1
        counts[f"predicted::{predicted}"] += 1
        if not ok:
            counts["mismatch"] += 1
            details.append(
                {
                    "id": case.get("id"),
                    "message": case["message"],
                    "expected": expected,
                    "expected_any": expected_any,
                    "predicted": predicted,
                }
            )

    return dict(counts), details


def print_report(counts: dict, mismatches: list[dict]) -> None:
    total = counts.get("total", 0)
    correct = counts.get("correct", 0)
    acc = (correct / total * 100.0) if total else 0.0

    print("Evaluation report")
    print("-----------------")
    print(f"Total:   {total}")
    print(f"Correct: {correct}")
    print(f"Acc:     {acc:.2f}%")
    print("")

    expected_keys = sorted(k for k in counts if k.startswith("expected::"))
    print("Expected distribution:")
    for key in expected_keys:
        print(f"- {key.split('::', 1)[1]}: {counts[key]}")
    print("")

    predicted_keys = sorted(k for k in counts if k.startswith("predicted::"))
    print("Predicted distribution:")
    for key in predicted_keys:
        print(f"- {key.split('::', 1)[1]}: {counts[key]}")

    if mismatches:
        print("")
        print("Mismatches:")
        for item in mismatches:
            print(
                f"- {item['id']}: expected={item['expected']} "
                f"expected_any={item.get('expected_any', [])} "
                f"predicted={item['predicted']} | {item['message']}"
            )


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python scripts/evaluate.py <cases.jsonl>")
        return 1

    cases_path = Path(sys.argv[1]).resolve()
    if not cases_path.exists():
        print(f"Cases file not found: {cases_path}")
        return 1

    seed_faq()
    cases = load_cases(cases_path)
    counts, mismatches = run_eval(cases)
    print_report(counts, mismatches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
