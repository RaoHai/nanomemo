"""Run evaluation experiments on LOCOMO dataset."""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.nanomemo_adapter import NanoMemoAdapter
from tqdm import tqdm


def load_locomo_dataset(dataset_path: str) -> dict:
    """Load LOCOMO dataset from JSON file."""
    with open(dataset_path) as f:
        return json.load(f)


def run_nanomemo_experiment(
    dataset: dict,
    memory_path: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Run NanoMemo evaluation on LOCOMO dataset.

    Args:
        dataset: LOCOMO dataset
        memory_path: Path to store memories
        model: OpenAI model to use

    Returns:
        Results dict with answers and metrics
    """
    adapter = NanoMemoAdapter(memory_path, model=model)
    results = defaultdict(list)

    for session_id, session_data in tqdm(dataset.items(), desc="Processing sessions"):
        # Process conversation turns
        conversation = session_data.get("conversation", [])
        print(f"\n[{session_id}] Processing {len(conversation)} conversation turns...")
        for i, turn in enumerate(tqdm(conversation, desc=f"  {session_id} turns", leave=False)):
            metrics = adapter.process_turn(turn, session_id)
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(conversation)} turns")

        # Answer questions
        for qa in session_data.get("questions", []):
            question = qa["question"]
            gold_answer = qa["answer"]
            category = qa.get("category", "unknown")

            # Skip category 5 (as per mem0 evaluation)
            if category == "5":
                continue

            answer_result = adapter.answer_question(question, session_id)

            results[session_id].append({
                "question": question,
                "answer": gold_answer,
                "response": answer_result["answer"],
                "category": category,
                "latency": answer_result["latency"],
                "tokens_used": answer_result["tokens_used"],
                "memories_retrieved": answer_result["memories_retrieved"],
            })

    return dict(results)


def main():
    parser = argparse.ArgumentParser(description="Run NanoMemo evaluation")
    parser.add_argument(
        "--dataset",
        type=str,
        default="dataset/locomo10.json",
        help="Path to LOCOMO dataset",
    )
    parser.add_argument(
        "--memory_path",
        type=str,
        default="./test_memory",
        help="Path to store memories",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="OpenAI model to use",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="results/nanomemo.json",
        help="Output file for results",
    )

    args = parser.parse_args()

    # Load dataset
    print(f"Loading dataset from {args.dataset}")
    dataset = load_locomo_dataset(args.dataset)
    print(f"Loaded {len(dataset)} sessions")

    # Run experiment
    print(f"Running NanoMemo evaluation...")
    start_time = time.time()
    results = run_nanomemo_experiment(
        dataset=dataset,
        memory_path=args.memory_path,
        model=args.model,
    )
    total_time = time.time() - start_time

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {output_path}")
    print(f"Total time: {total_time:.2f}s")

    # Print summary statistics
    total_questions = sum(len(v) for v in results.values())
    avg_latency = sum(
        item["latency"] for v in results.values() for item in v
    ) / total_questions
    avg_tokens = sum(
        item["tokens_used"] for v in results.values() for item in v
    ) / total_questions

    print(f"\nSummary:")
    print(f"  Total questions: {total_questions}")
    print(f"  Average latency: {avg_latency:.3f}s")
    print(f"  Average tokens: {avg_tokens:.1f}")


if __name__ == "__main__":
    main()
