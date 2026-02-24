"""Run LOCOMO evaluation with official format output."""

import argparse
import json
import sys
import time
from pathlib import Path

from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.simple_qa_adapter import SimpleQAAdapter


def load_official_dataset(dataset_path: str) -> list:
    """Load LOCOMO dataset in official format."""
    with open(dataset_path) as f:
        return json.load(f)


def convert_to_official_format(dataset_path: str) -> list:
    """Convert our format to official format."""
    with open(dataset_path) as f:
        data = json.load(f)

    official_data = []
    for session_id, session_data in data.items():
        sample = {
            "sample_id": session_id,
            "conversations": session_data.get("conversation", []),
            "qa": []
        }

        for qa in session_data.get("questions", []):
            sample["qa"].append({
                "question": qa["question"],
                "answer": qa["answer"],
                "category": int(qa.get("category", 0)),
                "evidence": qa.get("evidence", [])
            })

        official_data.append(sample)

    return official_data


def run_evaluation(
    dataset: list,
    memory_path: str,
    model: str = "gpt-4o-mini",
    model_key: str = "simple_qa"
) -> list:
    """Run evaluation and return results in official format."""
    adapter = SimpleQAAdapter(memory_path, model=model)
    results = []

    for sample in tqdm(dataset, desc="Processing samples"):
        sample_id = sample["sample_id"]
        conversations = sample["conversations"]

        print(f"\n[{sample_id}] Processing {len(conversations)} conversation turns...")

        # Process conversation turns
        for i, turn in enumerate(tqdm(conversations, desc=f"  {sample_id} turns", leave=False)):
            adapter.process_turn(turn, sample_id)
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(conversations)} turns")

        # Answer questions
        qa_results = []
        for qa in sample["qa"]:
            question = qa["question"]
            category = qa.get("category", 0)

            # Skip category 5 (as per official evaluation)
            if category == 5:
                continue

            answer_result = adapter.answer_question(question, sample_id)

            qa_results.append({
                "question": question,
                "answer": qa["answer"],
                "category": category,
                "evidence": qa.get("evidence", []),
                f"{model_key}_prediction": answer_result["answer"],
                "latency": answer_result["latency"],
                "tokens_used": answer_result["tokens_used"],
            })

        results.append({
            "sample_id": sample_id,
            "qa": qa_results
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Run LOCOMO evaluation with official format")
    parser.add_argument("--dataset", required=True, help="Path to LOCOMO dataset JSON")
    parser.add_argument("--memory_path", required=True, help="Path to memory directory")
    parser.add_argument("--output", required=True, help="Path to output results JSON")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")
    parser.add_argument("--model_key", default="simple_qa", help="Model key for results")
    parser.add_argument("--use_official_format", action="store_true",
                       help="Input is already in official format")

    args = parser.parse_args()

    print(f"Loading dataset from {args.dataset}")

    if args.use_official_format:
        dataset = load_official_dataset(args.dataset)
    else:
        dataset = convert_to_official_format(args.dataset)

    print(f"Loaded {len(dataset)} samples")

    print("Running evaluation...")
    start_time = time.time()

    results = run_evaluation(
        dataset=dataset,
        memory_path=args.memory_path,
        model=args.model,
        model_key=args.model_key
    )

    total_time = time.time() - start_time

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {args.output}")
    print(f"Total time: {total_time:.2f}s")

    # Print summary
    total_questions = sum(len(sample["qa"]) for sample in results)
    avg_latency = sum(q["latency"] for sample in results for q in sample["qa"]) / total_questions if total_questions > 0 else 0
    avg_tokens = sum(q["tokens_used"] for sample in results for q in sample["qa"]) / total_questions if total_questions > 0 else 0

    print(f"\nSummary:")
    print(f"  Total questions: {total_questions}")
    print(f"  Average latency: {avg_latency:.3f}s")
    print(f"  Average tokens: {avg_tokens:.1f}")


if __name__ == "__main__":
    main()
