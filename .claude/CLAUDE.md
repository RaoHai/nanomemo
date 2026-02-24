# NanoMemo Project Context

## Project Overview

NanoMemo is a structured, file-based long-term memory system for AI agents. It provides LLM-friendly storage and retrieval of knowledge across conversations.

## Core Architecture

### Memory System (`python/nanomemo/`)
- **File-based storage**: Markdown files with YAML frontmatter
- **SSOT principle**: One canonical file per entity
- **Summary-first search**: Efficient retrieval using frontmatter summaries
- **Categories**: people/, projects/, events/, daily/, credentials/, infra/, tools/

### Key Components
- `Memory` class: Core API for read/write/search operations
- Frontmatter: `summary`, `created`, `updated`, `tags`, `related`, `status`
- Search methods: `search_summaries()`, `search_tags()`, `search_content()`

## Evaluation Framework (`evaluation/`)

### Directory Structure
```
evaluation/
├── adapters/          # Memory system adapters
│   ├── simple_qa_adapter.py      # Baseline: stores full conversations
│   └── nanomemo_adapter.py       # Entity extraction approach
├── scripts/           # Evaluation runners
│   ├── run_simple_qa.py
│   └── run_experiments.py
├── dataset/           # LOCOMO benchmark data
├── results/           # Evaluation outputs (gitignored)
├── workspaces/        # Memory workspaces (gitignored)
└── tests/             # Test scripts
```

### LOCOMO Benchmark
- 10 sessions, ~4500 conversation turns
- 5 question categories: facts, temporal, preferences, relationships, context
- Metrics: accuracy, recall, F1, BLEU, ROUGE, BERTScore, LLM Judge

### Adapters

**SimpleQAAdapter** (baseline):
- Stores entire conversations in single files per session
- Uses full conversation context for QA
- Pros: Simple, effective
- Cons: High token usage (~600-1400 tokens/question)

**NanoMemoAdapter** (structured):
- Extracts entities/events/preferences via LLM
- Stores in categorized memory structure
- Pros: Structured knowledge, lower token usage
- Cons: Extraction quality varies, more complex

## Development Guidelines

### Environment Setup
```bash
# Python library
cd python
pip install -e .

# Evaluation
cd evaluation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
- `OPENAI_API_KEY`: Required for evaluation
- `OPENAI_BASE_URL`: Optional, defaults to OpenAI API

### Running Evaluations
```bash
# Simple QA baseline (fast, for testing)
python3 scripts/run_simple_qa.py \
  --dataset dataset/sample_locomo.json \
  --memory_path workspaces/test \
  --output results/test.json

# Full LOCOMO dataset
python3 scripts/run_simple_qa.py \
  --dataset dataset/locomo10_converted.json \
  --memory_path workspaces/full_test \
  --output results/full_test.json
```

## Important Notes

### Security
- **Never hardcode API keys** in code
- Always use environment variables
- API keys in git history have been cleaned (commit ad31c00)

### Git Workflow
- `results/` and `workspaces/` are gitignored
- Use `.gitkeep` to preserve directory structure
- Test files should read from environment variables only

### Code Quality
- Use grep fallback when ripgrep (rg) is not available
- Memory.read() returns content without frontmatter
- Memory.update() expects content without frontmatter
- Always handle FileNotFoundError for missing memory files

## Current Status

### Completed
- ✅ Core Memory class implementation
- ✅ LOCOMO dataset integration
- ✅ Simple QA baseline adapter
- ✅ NanoMemo entity extraction adapter
- ✅ Directory structure refactoring
- ✅ Documentation (README, STRUCTURE.md)
- ✅ Security cleanup (API key removal)

### Known Issues
- NanoMemo adapter: Entity extraction quality needs improvement
- Memory.update(): Multiple frontmatter blocks issue (fixed in simple_qa_adapter)
- Token usage: SimpleQA uses full conversation context (high cost)

### Next Steps
- Run full LOCOMO evaluation
- Implement metrics calculation (BLEU, ROUGE, etc.)
- Optimize entity extraction prompts
- Add LLM judge evaluation
- Compare with other memory systems (Mem0, Zep, etc.)

## Related Files

### Core Implementation
- `python/nanomemo/__init__.py` - Memory class
- `evaluation/adapters/simple_qa_adapter.py` - Baseline
- `evaluation/adapters/nanomemo_adapter.py` - Structured approach

### Documentation
- `README.md` - Project overview
- `evaluation/README.md` - Evaluation framework
- `evaluation/STRUCTURE.md` - Directory structure
- `evaluation/dataset/README.md` - Dataset info

### Configuration
- `.gitignore` - Root gitignore
- `evaluation/.gitignore` - Evaluation gitignore
- `python/pyproject.toml` - Python package config
- `evaluation/requirements.txt` - Evaluation dependencies
