"""Run LOCOMO evaluation with simple QA adapter."""

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tqdm import tqdm
from adapters.simple_qa_adapter import SimpleQAAdapter


def load_dataset(dataset_path: str) -> dict:
    """Load LOCOMO dataset."""
    with open(dataset_path) as f:
        return json.load(f)


def run_simple_qa_experiment(
    dataset: dict,
    memory_path: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """Run simple QA evaluation experiment."""
    adapter = SimpleQAAdapter(memory_path, model=model)
    results = defaultdict(list)

    start_time = time.time()

    for session_id, session_data in tqdm(dataset.items(), desc="Processing sessions"):
        # Process conversation turns
        conversation = session_data.get("conversation", [])
        print(f"\n[{session_id}] Processing {len(conversation)} conversation turns...")

        for i, turn in enumerate(tqdm(conversation, desc=f"  {session_id} turns", leave=False)):
            adapter.process_turn(turn, session_id)
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

    total_time = time.time() - start_time

    return dict(results), total_time


def main():
    parser = argparse.ArgumentParser(description="Run LOCOMO evaluation with simple QA")
    parser.add_argument("--dataset", required=True, help="Path to LOCOMO dataset JSON")
    parser.add_argument("--memory_path", required=True, help="Path to memory directory")
    parser.add_argument("--output", required=True, help="Path to output results JSON")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")

    args = parser.parse_args()

    print(f"Loading dataset from {args.dataset}")
    dataset = load_dataset(args.dataset)
    print(f"Loaded {len(dataset)} sessions")

    print("Running simple QA evaluation...")
    results, total_time = run_simple_qa_experiment(
        dataset=dataset,
        memory_path=args.memory_path,
        model=args.model,
    )

    # Save results
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to {args.output}")
    print(f"Total time: {total_time:.2f}s")

    # Print summary
    total_questions = sum(len(v) for v in results.values())
    avg_latency = sum(q["latency"] for v in results.values() for q in v) / total_questions if total_questions > 0 else 0
    avg_tokens = sum(q["tokens_used"] for v in results.values() for q in v) / total_questions if total_questions > 0 else 0

    print(f"\nSummary:")
    print(f"  Total questions: {total_questions}")
    print(f"  Average latency: {avg_latency:.3f}s")
    print(f"  Average tokens: {avg_tokens:.1f}")


if __name__ == "__main__":
    main()
