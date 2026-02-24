"""Calculate evaluation metrics from experiment results."""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from llm_judge import evaluate_llm_judge
from metrics import aggregate_metrics, calculate_metrics
from tqdm import tqdm


def evaluate_results(results_file: str, output_file: str) -> None:
    """
    Calculate metrics for experiment results.

    Args:
        results_file: Path to results JSON file
        output_file: Path to save metrics
    """
    with open(results_file) as f:
        results = json.load(f)

    all_metrics = []
    all_categories = []
    evaluated_results = defaultdict(list)

    print("Calculating metrics...")
    for session_id, items in tqdm(results.items()):
        for item in items:
            question = item["question"]
            gold_answer = item["answer"]
            response = item["response"]
            category = item["category"]

            # Calculate traditional metrics
            metrics = calculate_metrics(response, gold_answer)

            # Calculate LLM judge score
            llm_score = evaluate_llm_judge(question, gold_answer, response)

            # Store all metrics
            all_metrics.append(metrics)
            all_categories.append(category)

            evaluated_results[session_id].append({
                **item,
                **metrics,
                "llm_score": llm_score,
            })

    # Aggregate metrics
    print("Aggregating metrics...")
    aggregated = aggregate_metrics(all_metrics, all_categories)

    # Add LLM scores to aggregation
    llm_scores_by_category = defaultdict(list)
    for session_items in evaluated_results.values():
        for item in session_items:
            llm_scores_by_category[item["category"]].append(item["llm_score"])

    aggregated["overall"]["llm_score"] = {
        "mean": sum(s for scores in llm_scores_by_category.values() for s in scores)
        / sum(len(scores) for scores in llm_scores_by_category.values()),
    }

    for category, scores in llm_scores_by_category.items():
        if f"category_{category}" in aggregated:
            aggregated[f"category_{category}"]["llm_score"] = {
                "mean": sum(scores) / len(scores) if scores else 0.0,
                "count": len(scores),
            }

    # Save detailed results
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({
            "aggregated_metrics": aggregated,
            "detailed_results": dict(evaluated_results),
        }, f, indent=2)

    print(f"\nMetrics saved to {output_path}")

    # Print summary
    print("\n=== Overall Metrics ===")
    for metric, stats in aggregated["overall"].items():
        if isinstance(stats, dict) and "mean" in stats:
            print(f"{metric:20s}: {stats['mean']:.4f}")

    print("\n=== Per-Category LLM Scores ===")
    for category in sorted(llm_scores_by_category.keys()):
        scores = llm_scores_by_category[category]
        accuracy = sum(scores) / len(scores) if scores else 0.0
        print(f"Category {category}: {accuracy:.4f} ({sum(scores)}/{len(scores)})")


def main():
    parser = argparse.ArgumentParser(description="Evaluate experiment results")
    parser.add_argument(
        "--input_file",
        type=str,
        required=True,
        help="Path to results JSON file",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        required=True,
        help="Path to save metrics",
    )

    args = parser.parse_args()

    evaluate_results(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
