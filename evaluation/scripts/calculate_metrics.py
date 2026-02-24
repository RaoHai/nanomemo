"""Calculate metrics using official LOCOMO evaluation code."""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation import eval_question_answering
from evaluation_stats import analyze_aggr_acc


def main():
    parser = argparse.ArgumentParser(description="Calculate LOCOMO evaluation metrics")
    parser.add_argument("--input", required=True, help="Path to results JSON file")
    parser.add_argument("--output", required=True, help="Path to output stats JSON file")
    parser.add_argument("--model_key", default="simple_qa", help="Model key in results")
    parser.add_argument("--data_file", help="Original data file (optional)")

    args = parser.parse_args()

    print(f"Loading results from {args.input}")
    with open(args.input) as f:
        results = json.load(f)

    print(f"Calculating metrics for model: {args.model_key}")

    # Calculate F1 scores for each sample
    prediction_key = f"{args.model_key}_prediction"
    f1_key = f"{args.model_key}_f1"

    for sample in results:
        exact_matches, lengths, recall = eval_question_answering(
            sample["qa"],
            prediction_key
        )

        for i, qa in enumerate(sample["qa"]):
            qa[f1_key] = round(exact_matches[i], 3)

    # Save updated results with F1 scores
    with open(args.input, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Updated results saved to {args.input}")

    # Calculate aggregate statistics
    if args.data_file:
        print(f"Calculating aggregate statistics...")
        analyze_aggr_acc(
            args.data_file,
            args.input,
            args.output,
            args.model_key,
            f1_key,
            rag=False
        )
        print(f"Statistics saved to {args.output}")
    else:
        # Calculate basic statistics without original data file
        total_questions = sum(len(sample["qa"]) for sample in results)
        avg_f1 = sum(qa.get(f1_key, 0) for sample in results for qa in sample["qa"]) / total_questions if total_questions > 0 else 0

        stats = {
            "model": args.model_key,
            "total_questions": total_questions,
            "average_f1": round(avg_f1, 4)
        }

        # Calculate per-category F1
        category_stats = {}
        for sample in results:
            for qa in sample["qa"]:
                cat = qa.get("category", 0)
                if cat not in category_stats:
                    category_stats[cat] = {"count": 0, "f1_sum": 0}
                category_stats[cat]["count"] += 1
                category_stats[cat]["f1_sum"] += qa.get(f1_key, 0)

        stats["per_category"] = {}
        for cat, data in category_stats.items():
            stats["per_category"][f"category_{cat}"] = {
                "count": data["count"],
                "average_f1": round(data["f1_sum"] / data["count"], 4) if data["count"] > 0 else 0
            }

        with open(args.output, "w") as f:
            json.dump(stats, f, indent=2)

        print(f"\nBasic statistics saved to {args.output}")
        print(f"Average F1: {avg_f1:.4f}")


if __name__ == "__main__":
    main()
