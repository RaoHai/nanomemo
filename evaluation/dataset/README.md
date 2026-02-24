# LOCOMO Dataset

## Overview

The **LOCOMO** (Long-term Conversational Memory) dataset is designed to evaluate memory systems for AI agents. It contains multi-turn conversations followed by memory-dependent questions.

## Dataset Structure

Each session contains:
- `conversation`: List of conversation turns with speaker and content
- `questions`: List of questions with ground truth answers and categories

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

The complete LOCOMO dataset used in the mem0 paper can be downloaded from:

**Google Drive**: https://drive.google.com/drive/folders/1L-cTjTm0ohMsitsHg4dijSPJtqNflwX-

Files:
- `locomo10.json`: Original dataset with 10 sessions
- `locomo10_rag.json`: Formatted for RAG experiments

Place downloaded files in this `dataset/` directory.

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
# Run evaluation on sample dataset
python run_experiments.py \
  --dataset dataset/sample_locomo.json \
  --memory_path ./test_memory \
  --output results/nanomemo_sample.json

# Calculate metrics
python evals.py \
  --input_file results/nanomemo_sample.json \
  --output_file metrics/nanomemo_sample_metrics.json
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
