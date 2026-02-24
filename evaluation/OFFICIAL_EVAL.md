# Using Official LOCOMO Evaluation

We now use the official LOCOMO evaluation code from https://github.com/snap-research/locomo

## Quick Start

### 1. Run Evaluation

```bash
# Activate virtual environment
source venv/bin/activate

# Run evaluation (generates predictions)
python3 scripts/run_official_eval.py \
  --dataset dataset/sample_locomo.json \
  --memory_path workspaces/test \
  --output results/test.json \
  --model_key simple_qa

# Calculate metrics (F1, etc.)
python3 scripts/calculate_metrics.py \
  --input results/test.json \
  --output results/test_stats.json \
  --model_key simple_qa
```

### 2. Full LOCOMO Dataset

```bash
# Run on full dataset (takes longer)
python3 scripts/run_official_eval.py \
  --dataset dataset/locomo10_converted.json \
  --memory_path workspaces/full_test \
  --output results/full_test.json \
  --model_key simple_qa

# Calculate metrics
python3 scripts/calculate_metrics.py \
  --input results/full_test.json \
  --output results/full_test_stats.json \
  --model_key simple_qa
```

## Output Format

### Results JSON
```json
[
  {
    "sample_id": "session_000",
    "qa": [
      {
        "question": "When did Caroline go to the LGBTQ support group?",
        "answer": "7 May 2023",
        "category": 2,
        "evidence": ["D1:3"],
        "simple_qa_prediction": "Caroline went yesterday.",
        "simple_qa_f1": 0.0,
        "latency": 1.23,
        "tokens_used": 628
      }
    ]
  }
]
```

### Statistics JSON
```json
{
  "model": "simple_qa",
  "total_questions": 20,
  "average_f1": 0.0566,
  "per_category": {
    "category_1": {"count": 6, "average_f1": 0.0278},
    "category_2": {"count": 11, "average_f1": 0.0},
    "category_3": {"count": 1, "average_f1": 0.133},
    "category_4": {"count": 2, "average_f1": 0.416}
  }
}
```

## Metrics

The official evaluation calculates:
- **F1 Score**: Token-level F1 between prediction and ground truth
- **Per-category F1**: F1 scores broken down by question category
- **Average F1**: Overall F1 across all questions

Categories:
1. Factual Recall
2. Temporal Reasoning
3. Preference Memory
4. Relationship Memory
5. Contextual Understanding (excluded from evaluation)

## Files

- `evaluation.py` - Official LOCOMO evaluation code
- `evaluation_stats.py` - Official statistics calculation
- `scripts/run_official_eval.py` - Our evaluation runner
- `scripts/calculate_metrics.py` - Metrics calculator wrapper
