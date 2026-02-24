# NanoMemo Evaluation Framework

Benchmark suite for evaluating NanoMemo against other memory systems.

## Overview

This evaluation framework tests memory systems on their ability to:
1. **Store** information accurately from conversations
2. **Retrieve** relevant information when needed
3. **Update** existing memories correctly
4. **Scale** with growing memory size

## Evaluation Metrics

### 1. Retrieval Accuracy
- **Precision**: Percentage of retrieved memories that are relevant
- **Recall**: Percentage of relevant memories that were retrieved
- **F1 Score**: Harmonic mean of precision and recall

### 2. Response Quality
- **BLEU Score**: N-gram overlap with ground truth answers
- **ROUGE Score**: Recall-oriented overlap metrics
- **BERTScore**: Semantic similarity using embeddings
- **LLM Judge**: Binary correctness evaluation by GPT-4

### 3. Performance
- **Latency**: Time to search and retrieve memories
- **Token Consumption**: Tokens used in memory operations
- **Storage Efficiency**: Disk space per memory entry

### 4. Consistency
- **SSOT Compliance**: Single source of truth maintained
- **Update Accuracy**: Correct updates without duplication
- **Link Integrity**: Related links remain valid

## Dataset

We use the **LOCOMO** (Long-term Conversational Memory) dataset, which contains:
- Multi-turn conversations with memory-dependent questions
- 5 question categories testing different memory aspects
- Ground truth answers for evaluation

### Question Categories
1. **Factual Recall**: Direct facts from conversation
2. **Temporal Reasoning**: Time-based queries
3. **Preference Memory**: User preferences and habits
4. **Relationship Memory**: Connections between entities
5. **Contextual Understanding**: Inferred information

## Baseline Comparisons

We compare NanoMemo against:

1. **Full Context**: Entire conversation history in context window
2. **RAG Systems**: Vector-based retrieval with various chunk sizes
3. **Mem0**: Graph-based memory with LLM extraction
4. **LangMem**: Language model-based memory management
5. **Zep**: Specialized memory infrastructure
6. **OpenAI Memory**: Built-in ChatGPT memory feature

## Running Evaluations

### Setup

```bash
cd nanomemo/evaluation
pip install -r requirements.txt

# Download LOCOMO dataset
# Place in dataset/ directory
```

### Run Experiments

```bash
# Evaluate NanoMemo
python run_experiments.py --method nanomemo --output results/nanomemo.json

# Evaluate baseline (full context)
python run_experiments.py --method full_context --output results/full_context.json

# Evaluate RAG
python run_experiments.py --method rag --chunk_size 500 --top_k 3 --output results/rag_500_k3.json
```

### Generate Scores

```bash
# Calculate metrics for all results
python evals.py --input_file results/nanomemo.json --output_file metrics/nanomemo_metrics.json

# Generate comparison report
python generate_scores.py --results_dir results/ --output comparison.md
```

## Evaluation Protocol

### 1. Memory Building Phase
- Process conversation turns sequentially
- Store information using each system's method
- Track storage operations and latency

### 2. Query Phase
- Ask memory-dependent questions
- Retrieve relevant information
- Generate answers using retrieved context

### 3. Scoring Phase
- Compare generated answers with ground truth
- Calculate all metrics
- Aggregate by category and overall

## Expected Results

Based on NanoMemo's design, we expect:

**Strengths:**
- High SSOT compliance (no duplication)
- Fast summary-first retrieval
- Low token consumption (only relevant memories loaded)
- Excellent update accuracy (direct file editing)

**Trade-offs:**
- May require more explicit entity extraction
- Depends on quality of frontmatter summaries
- Less automatic than embedding-based systems

## Implementation Details

### NanoMemo Adapter

```python
class NanoMemoAdapter:
    def __init__(self, memory_path: str):
        self.memory = Memory(memory_path)
        self.llm = OpenAI()  # For entity extraction

    def process_turn(self, turn: dict) -> None:
        """Process a conversation turn and store memories."""
        # Extract entities and facts
        entities = self._extract_entities(turn["content"])

        # Store in appropriate categories
        for entity in entities:
            self._store_entity(entity)

    def answer_question(self, question: str) -> str:
        """Answer a question using memory."""
        # Search summaries first
        results = self.memory.search_summaries(question)

        # Read relevant files
        context = []
        for result in results[:5]:  # Top 5
            content = self.memory.read(result.path)
            context.append(content)

        # Generate answer with context
        return self._generate_answer(question, context)
```

## Citation

If you use this evaluation framework, please cite:

```bibtex
@software{nanomemo2026,
  title={NanoMemo: Structured Long-Term Memory for AI Agents},
  author={NanoMemo Contributors},
  year={2026},
  url={https://github.com/nanomemo/nanomemo}
}
```

## License

MIT
