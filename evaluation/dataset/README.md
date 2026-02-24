# LOCOMO Dataset

## Overview

The **LOCOMO** (Long-term Conversational Memory) dataset is designed to evaluate memory systems for AI agents. It contains multi-turn conversations followed by memory-dependent questions.

## Included Datasets

### 1. Full LOCOMO Dataset ✅
- **File**: `locomo10.json` (original format)
- **File**: `locomo10_converted.json` (simplified format for evaluation)
- **Size**: 10 conversations, 1,542 questions
- **Format**: Multi-session conversations with evidence-linked QA pairs

### 2. Sample Dataset
- **File**: `sample_locomo.json`
- **Size**: 3 conversations, 17 questions
- **Purpose**: Quick testing and development

## Dataset Structure

### Converted Format (`locomo10_converted.json`)

Each session contains:
- `conversation`: List of conversation turns with speaker and content
- `questions`: List of questions with ground truth answers and categories
- `speaker_a`, `speaker_b`: Names of the two speakers

```json
{
  "session_001": {
    "conversation": [
      {
        "speaker": "Caroline",
        "content": "Hey Mel! Good to see you!",
        "dia_id": "D1:1"
      }
    ],
    "questions": [
      {
        "question": "When did Caroline go to the LGBTQ support group?",
        "answer": "7 May 2023",
        "category": "2",
        "evidence": ["D1:3"]
      }
    ],
    "speaker_a": "Caroline",
    "speaker_b": "Melanie"
  }
}
```

### Question Categories

1. **Category 1 - Factual Recall**: Direct facts mentioned in conversation
   - Example: "What is my name?" → "Alice"

2. **Category 2 - Temporal Reasoning**: Time-related queries
   - Example: "When did I go to Hawaii?" → "Last month"

3. **Category 3 - Preference Memory**: User preferences and habits
   - Example: "Do I prefer TypeScript or JavaScript?" → "TypeScript"

4. **Category 4 - Relationship Memory**: Connections between entities
   - Example: "Who is helping with frontend?" → "Bob"

5. **Category 5 - Contextual Understanding**: Inferred information (excluded from evaluation)

## Sample Dataset

We provide `sample_locomo.json` with 3 sessions and 17 questions for testing the evaluation pipeline.

## Full LOCOMO Dataset

The complete LOCOMO dataset is **included** in this repository:
- `locomo10.json`: Original format from mem0 paper
- `locomo10_converted.json`: Simplified format ready for evaluation

No additional download required!

## Citation

The LOCOMO dataset was introduced in:

```bibtex
@article{mem0,
  title={Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory},
  author={Chhikara, Prateek and Khant, Dev and Aryan, Saket and Singh, Taranjeet and Yadav, Deshraj},
  journal={arXiv preprint arXiv:2504.19413},
  year={2025}
}
```

## Usage

```bash
# Run evaluation on full LOCOMO dataset
python run_experiments.py \
  --dataset dataset/locomo10_converted.json \
  --memory_path ./test_memory \
  --output results/nanomemo_full.json

# Run on sample dataset (faster, for testing)
python run_experiments.py \
  --dataset dataset/sample_locomo.json \
  --memory_path ./test_memory_sample \
  --output results/nanomemo_sample.json

# Calculate metrics
python evals.py \
  --input_file results/nanomemo_full.json \
  --output_file metrics/nanomemo_full_metrics.json
```

## Converting Dataset Format

If you need to re-convert the original format:

```bash
python convert_dataset.py \
  --input dataset/locomo10.json \
  --output dataset/locomo10_converted.json
```

## Expected Format

```json
{
  "session_id": {
    "conversation": [
      {
        "speaker": "user" | "assistant",
        "content": "..."
      }
    ],
    "questions": [
      {
        "question": "...",
        "answer": "...",
        "category": "1" | "2" | "3" | "4" | "5"
      }
    ]
  }
}
```

## Creating Custom Datasets

You can create your own evaluation datasets following the same format. Guidelines:

1. **Conversations**: Include 5-10 turns with factual information
2. **Questions**: Mix different categories to test various memory aspects
3. **Answers**: Keep ground truth concise and specific
4. **Categories**: Assign appropriate category numbers

Example conversation topics:
- Personal information (name, job, location)
- Events and activities (trips, meetings, projects)
- Preferences and habits (tools, schedules, likes/dislikes)
- Relationships (colleagues, friends, family)
- Projects and work (status, goals, technologies)
