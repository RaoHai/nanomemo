# NanoMemo Python Library

Python implementation of NanoMemo memory operations.

## Installation

```bash
pip install nanomemo
```

## Quick Start

```python
from nanomemo import Memory

# Initialize memory
memory = Memory("./memory")

# Search summaries
results = memory.search_summaries("API v2")
for result in results:
    print(f"{result.path}: {result.summary}")

# Read memory file
content = memory.read("projects/api-v2.md")
print(content)

# Write memory file
memory.write(
    path="people/charlie.md",
    content="# Charlie\n\nBackend engineer...",
    summary="Charlie - Backend engineer, Python specialist",
    tags=["people", "engineering"]
)

# List category
files = memory.list_category("people")
print(files)
```

## API Reference

### Memory Class

```python
class Memory:
    def __init__(self, base_path: str):
        """Initialize memory with base directory path."""

    def search_summaries(self, query: str, case_sensitive: bool = False) -> List[SearchResult]:
        """Search memory file summaries for query string."""

    def search_tags(self, tag: str) -> List[SearchResult]:
        """Search memory files by tag."""

    def search_content(self, query: str, case_sensitive: bool = False) -> List[SearchResult]:
        """Full-text search across all memory files."""

    def read(self, path: str) -> str:
        """Read a memory file."""

    def write(
        self,
        path: str,
        content: str,
        summary: str,
        tags: Optional[List[str]] = None,
        related: Optional[List[str]] = None,
        status: Optional[str] = None
    ) -> None:
        """Write a memory file with frontmatter."""

    def update(self, path: str, content: str, update_timestamp: bool = True) -> None:
        """Update an existing memory file."""

    def delete(self, path: str) -> None:
        """Delete a memory file."""

    def list_category(self, category: str) -> List[str]:
        """List all files in a category."""

    def get_metadata(self, path: str) -> Dict[str, Any]:
        """Extract frontmatter metadata from a memory file."""
```

### SearchResult Class

```python
@dataclass
class SearchResult:
    path: str           # Relative path to memory file
    summary: str        # Summary from frontmatter
    tags: List[str]     # Tags from frontmatter
    created: str        # Creation date
    updated: Optional[str]  # Last update date
```

## Examples

### Proactive Entity Fetching

```python
def process_message(message: str, memory: Memory):
    # Extract entity mentions
    entities = extract_entities(message)  # Your NER logic

    # Fetch relevant memories
    context = []
    for entity in entities:
        results = memory.search_summaries(entity)
        for result in results:
            content = memory.read(result.path)
            context.append(content)

    # Use context in LLM prompt
    prompt = build_prompt(message, context)
    response = llm.generate(prompt)
    return response
```

### Saving New Information

```python
def save_person_profile(name: str, info: dict, memory: Memory):
    content = f"""# {name}

## Role
{info['role']}

## Preferences
{chr(10).join(f"- {pref}" for pref in info['preferences'])}

## Notes
{info['notes']}
"""

    memory.write(
        path=f"people/{name.lower().replace(' ', '-')}.md",
        content=content,
        summary=f"{name} - {info['role']}",
        tags=["people"] + info.get('tags', [])
    )
```

### Daily Log Entry

```python
from datetime import datetime

def add_daily_entry(event: str, memory: Memory):
    today = datetime.now().strftime("%Y-%m-%d")
    path = f"daily/{today}.md"

    # Check if today's log exists
    try:
        content = memory.read(path)
        # Append to existing log
        content += f"\n- {datetime.now().strftime('%H:%M')} - {event}"
        memory.update(path, content)
    except FileNotFoundError:
        # Create new daily log
        content = f"""# {today}

## Events
- {datetime.now().strftime('%H:%M')} - {event}
"""
        memory.write(
            path=path,
            content=content,
            summary=f"{today} - Daily log",
            tags=["daily"]
        )
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy nanomemo

# Linting
ruff check nanomemo
```

## License

MIT
