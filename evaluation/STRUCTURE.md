# Evaluation Directory Structure

```
evaluation/
├── adapters/              # Memory system adapters for evaluation
│   ├── nanomemo_adapter.py    # NanoMemo with entity extraction
│   └── simple_qa_adapter.py   # Simple baseline QA system
│
├── scripts/               # Evaluation scripts
│   ├── run_experiments.py     # Run NanoMemo evaluation
│   ├── run_simple_qa.py       # Run simple QA baseline
│   └── convert_dataset.py     # Convert LOCOMO dataset format
│
├── dataset/               # LOCOMO benchmark datasets
│   ├── locomo10.json          # Original LOCOMO dataset (10 sessions)
│   ├── locomo10_converted.json # Converted format
│   ├── sample_locomo.json     # Small sample (2 sessions, 20 turns each)
│   └── README.md
│
├── results/               # Evaluation results (JSON)
│   ├── nanomemo_sample.json
│   └── simple_qa_sample.json
│
├── workspaces/            # Memory workspaces (gitignored)
│   ├── test_memory/
│   ├── test_memory_sample/
│   └── test_memory_simple/
│
├── tests/                 # Test scripts
│   ├── test_api.py
│   └── test_memory.py
│
├── venv/                  # Python virtual environment
│
├── metrics.py             # Evaluation metrics (BLEU, ROUGE, etc.)
├── llm_judge.py           # LLM-based evaluation
├── evals.py               # Evaluation utilities
├── requirements.txt       # Python dependencies
└── README.md              # Main documentation
```

## Quick Start

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional
```

### 3. Run Evaluation

**Simple QA Baseline (recommended for testing):**
```bash
python3 scripts/run_simple_qa.py \
  --dataset dataset/sample_locomo.json \
  --memory_path workspaces/simple_qa_test \
  --output results/simple_qa_test.json
```

**NanoMemo with Entity Extraction:**
```bash
python3 scripts/run_experiments.py \
  --dataset dataset/sample_locomo.json \
  --memory_path workspaces/nanomemo_test \
  --output results/nanomemo_test.json
```

## Adapters

### SimpleQAAdapter
- **Approach**: Store entire conversations, use full context for QA
- **Pros**: Simple, effective baseline
- **Cons**: High token usage (~1400 tokens/question)

### NanoMemoAdapter
- **Approach**: Extract entities/facts via LLM, store structured memory
- **Pros**: Lower token usage, structured knowledge
- **Cons**: Extraction quality depends on LLM, more complex

## Datasets

- `locomo10.json` - Full LOCOMO dataset (10 sessions, ~4500 turns)
- `sample_locomo.json` - Small sample for testing (2 sessions, 40 turns)

## Results Format

```json
{
  "session_000": [
    {
      "question": "When did Caroline go to the LGBTQ support group?",
      "answer": "7 May 2023",
      "response": "Caroline went yesterday.",
      "category": "2",
      "latency": 1.23,
      "tokens_used": 1387,
      "memories_retrieved": 1
    }
  ]
}
```
