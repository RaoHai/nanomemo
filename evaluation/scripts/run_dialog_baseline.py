"""Run official LOCOMO evaluation using their evaluate_qa.py approach."""

import argparse
import json
import os
import sys
from pathlib import Path

from tqdm import tqdm
from openai import OpenAI

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from evaluation import eval_question_answering
from evaluation_stats import analyze_aggr_acc


# Official prompt from LOCOMO
QA_PROMPT = """
Based on the above context, write an answer in the form of a short phrase for the following question. Answer with exact words from the context whenever possible.

Question: {} Short answer:
"""

CONV_START_PROMPT = "Below is a conversation between two people: {} and {}. The conversation takes place over multiple days.\n\n"


def format_conversation(conversations, speaker_a="Speaker A", speaker_b="Speaker B"):
    """Format conversation in official LOCOMO style."""
    conv_text = CONV_START_PROMPT.format(speaker_a, speaker_b)

    for turn in conversations:
        speaker = turn.get("speaker", "Unknown")
        content = turn.get("content", "")
        conv_text += f"{speaker}: {content}\n"

    return conv_text


def truncate_conversation(conv_text, max_tokens=120000):
    """Truncate conversation to fit within token limit."""
    # Simple truncation - take last N characters
    # In production, should use tiktoken for accurate token counting
    max_chars = max_tokens * 4  # Rough estimate: 1 token ≈ 4 chars
    if len(conv_text) > max_chars:
        conv_text = "...[earlier conversation truncated]...\n\n" + conv_text[-max_chars:]
    return conv_text


def run_official_eval(dataset_path, output_path, model="gpt-4o-mini"):
    """Run evaluation using official LOCOMO approach."""

    # Initialize OpenAI client
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # Load dataset
    with open(dataset_path) as f:
        dataset = json.load(f)

    # Convert to list format if dict
    if isinstance(dataset, dict):
        dataset = [
            {
                "sample_id": sid,
                "conversations": sdata.get("conversation", []),
                "qa": [
                    {
                        "question": qa["question"],
                        "answer": qa["answer"],
                        "category": int(qa.get("category", 0)),
                        "evidence": qa.get("evidence", [])
                    }
                    for qa in sdata.get("questions", [])
                ],
                "speaker_a": sdata.get("speaker_a", "Speaker A"),
                "speaker_b": sdata.get("speaker_b", "Speaker B")
            }
            for sid, sdata in dataset.items()
        ]

    # Load existing results if available
    if os.path.exists(output_path):
        with open(output_path) as f:
            out_samples = {d['sample_id']: d for d in json.load(f)}
    else:
        out_samples = {}

    model_key = model.replace("-", "_").replace(".", "_")
    prediction_key = f"{model_key}_prediction"

    # Process each sample
    for data in tqdm(dataset, desc="Processing samples"):
        sample_id = data['sample_id']

        # Check if already processed
        if sample_id in out_samples:
            out_data = out_samples[sample_id]
        else:
            out_data = {
                'sample_id': sample_id,
                'qa': data['qa'].copy()
            }

        # Format conversation
        conv_text = format_conversation(
            data['conversations'],
            data.get('speaker_a', 'Speaker A'),
            data.get('speaker_b', 'Speaker B')
        )
        conv_text = truncate_conversation(conv_text)

        # Answer each question
        for i, qa in enumerate(out_data['qa']):
            # Skip if already answered
            if prediction_key in qa:
                continue

            # Skip category 5
            if qa.get('category') == 5:
                continue

            # Build prompt
            prompt = conv_text + "\n" + QA_PROMPT.format(qa['question'])

            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.0,
                    max_tokens=50
                )

                answer = response.choices[0].message.content.strip()
                qa[prediction_key] = answer

            except Exception as e:
                print(f"Error answering question: {e}")
                qa[prediction_key] = "Error"

        out_samples[sample_id] = out_data

        # Save incrementally
        with open(output_path, 'w') as f:
            json.dump(list(out_samples.values()), f, indent=2)

    # Calculate F1 scores
    print("\nCalculating F1 scores...")
    for sample in out_samples.values():
        exact_matches, lengths, recall = eval_question_answering(
            sample["qa"],
            prediction_key
        )

        for i, qa in enumerate(sample["qa"]):
            qa[f"{model_key}_f1"] = round(exact_matches[i], 3)

    # Save final results
    with open(output_path, 'w') as f:
        json.dump(list(out_samples.values()), f, indent=2)

    # Calculate statistics
    stats_path = output_path.replace('.json', '_stats.json')
    total_questions = sum(len(sample["qa"]) for sample in out_samples.values())
    avg_f1 = sum(
        qa.get(f"{model_key}_f1", 0)
        for sample in out_samples.values()
        for qa in sample["qa"]
    ) / total_questions if total_questions > 0 else 0

    # Per-category stats
    category_stats = {}
    for sample in out_samples.values():
        for qa in sample["qa"]:
            cat = qa.get("category", 0)
            if cat not in category_stats:
                category_stats[cat] = {"count": 0, "f1_sum": 0}
            category_stats[cat]["count"] += 1
            category_stats[cat]["f1_sum"] += qa.get(f"{model_key}_f1", 0)

    stats = {
        "model": model,
        "total_questions": total_questions,
        "average_f1": round(avg_f1, 4),
        "per_category": {}
    }

    for cat, data in category_stats.items():
        stats["per_category"][f"category_{cat}"] = {
            "count": data["count"],
            "average_f1": round(data["f1_sum"] / data["count"], 4) if data["count"] > 0 else 0
        }

    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"\nResults saved to {output_path}")
    print(f"Statistics saved to {stats_path}")
    print(f"Average F1: {avg_f1:.4f}")


def main():
    parser = argparse.ArgumentParser(description="Run official LOCOMO evaluation")
    parser.add_argument("--dataset", required=True, help="Path to dataset")
    parser.add_argument("--output", required=True, help="Path to output file")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model to use")

    args = parser.parse_args()

    run_official_eval(args.dataset, args.output, args.model)


if __name__ == "__main__":
    main()
