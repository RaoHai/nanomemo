"""Convert LOCOMO dataset to simplified format for evaluation."""

import json
from pathlib import Path


def convert_locomo_to_simple_format(locomo_path: str, output_path: str) -> None:
    """
    Convert LOCOMO dataset to simplified session format.

    Args:
        locomo_path: Path to locomo10.json
        output_path: Path to save converted dataset
    """
    with open(locomo_path) as f:
        data = json.load(f)

    converted = {}

    for idx, item in enumerate(data):
        session_id = f"session_{idx:03d}"
        conversation = item["conversation"]
        qa_pairs = item["qa"]

        # Extract all dialogue turns from all sessions
        turns = []
        for key in sorted(conversation.keys()):
            if key.startswith("session_") and not key.endswith("_date_time"):
                session_turns = conversation[key]
                if session_turns:  # Some sessions might be empty
                    for turn in session_turns:
                        turns.append({
                            "speaker": turn["speaker"],
                            "content": turn["text"],
                            "dia_id": turn.get("dia_id", ""),
                        })

        # Convert QA pairs
        questions = []
        for qa in qa_pairs:
            # Skip QA pairs without answer
            if "answer" not in qa:
                continue
            questions.append({
                "question": qa.get("question", ""),
                "answer": str(qa["answer"]),
                "category": str(qa.get("category", "0")),
                "evidence": qa.get("evidence", []),
            })

        converted[session_id] = {
            "conversation": turns,
            "questions": questions,
            "speaker_a": conversation.get("speaker_a", ""),
            "speaker_b": conversation.get("speaker_b", ""),
        }

    # Save converted dataset
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(converted, f, indent=2)

    print(f"Converted {len(data)} conversations")
    print(f"Total questions: {sum(len(v['questions']) for v in converted.values())}")
    print(f"Saved to {output_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert LOCOMO dataset format")
    parser.add_argument(
        "--input",
        type=str,
        default="dataset/locomo10.json",
        help="Path to original LOCOMO dataset",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="dataset/locomo10_converted.json",
        help="Path to save converted dataset",
    )

    args = parser.parse_args()

    convert_locomo_to_simple_format(args.input, args.output)
