# NanoMemo

A structured, LLM-friendly long-term memory system for AI agents.

## Overview

NanoMemo provides a file-based memory architecture that allows AI agents to:
- Store and retrieve structured knowledge across conversations
- Maintain single source of truth (SSOT) for entities
- Search efficiently using summary-first approach
- Prevent hallucinations by grounding responses in saved facts

## Core Principles

1. **Single Source of Truth (SSOT)**: Each entity (person, project, system) has exactly one canonical file
2. **Related Links**: Cross-references use frontmatter `related:` fields instead of duplication
3. **Tag System**: Support cross-domain search with structured tags
4. **Search First**: When uncertain, search memory; if not found, admit it
5. **Proactive Sniffing**: Automatically fetch entity profiles when they appear in conversation

## Directory Structure

```
memory/
├── MEMORY.md           # Index file (read-only for agents)
├── people/             # Person profiles
├── projects/           # Project information
├── events/             # Important events
├── credentials/        # Sensitive credentials
├── infra/              # Infrastructure configs
├── daily/              # Daily logs (YYYY-MM-DD.md)
├── mistakes.md         # Error log
└── tools/              # Tool preferences
```

## Frontmatter Format

Every memory file must include frontmatter with at least a `summary` field:

```yaml
---
summary: "One-line description with key entities and context"
created: 2026-02-24
updated: 2026-02-24
status: in-progress     # Optional: in-progress | resolved | blocked | abandoned
tags: [ai, memory]      # Optional: for cross-domain search
related: [people/alice.md]  # Optional: related files
---

# Content

Your memory content here...
```

## Search Workflow

NanoMemo uses a **summary-first** approach for efficient search:

```bash
# 1. List categories
ls memory/

# 2. View all summaries
rg "^summary:" memory/ --no-ignore --hidden

# 3. Search summaries by keyword
rg "^summary:.*keyword" memory/ --no-ignore --hidden -i

# 4. Search by tag
rg "^tags:.*keyword" memory/ --no-ignore --hidden -i

# 5. Full-text search (when summary search isn't enough)
rg "keyword" memory/ --no-ignore --hidden -i

# 6. Read specific file if relevant
cat memory/path/to/file.md
```

**Note**: Memory files are typically gitignored, so use `--no-ignore` and `--hidden` flags.

## Operations

### Save Memory

```bash
# Determine category and filename
mkdir -p memory/category/

# Write with frontmatter
cat > memory/category/filename.md << 'EOF'
---
summary: "Brief description"
created: $(date +%Y-%m-%d)
---

# Title

Content...
EOF
```

### Update Memory

When information changes:
1. Update the content
2. Add `updated: YYYY-MM-DD` to frontmatter
3. Update `status` if applicable

### Maintain Memory

- **Delete**: Remove obsolete files
- **Consolidate**: Merge related memories when they grow
- **Reorganize**: Move files to better-fitting categories

## Integration with AI Agents

### 1. System Prompt Injection

Include `MEMORY.md` in the agent's system prompt to provide:
- Memory structure overview
- Operation guidelines
- Tag ontology
- Entity directory

### 2. Tool/Skill Definition

Provide agents with memory operations:
- `search_memory(query)` - Search summaries and content
- `read_memory(path)` - Read specific memory file
- `write_memory(path, content)` - Create or update memory
- `list_memories(category)` - List files in category

### 3. Proactive Memory Usage

Agents should automatically:
- **On entity mention**: Fetch relevant memory files
- **On ambiguous reference**: Search memory for context
- **On new information**: Save to appropriate category
- **On preference question**: Check memory before asking user

### 4. Hallucination Prevention

When memory search returns no results:
- Agent must say "I don't have information about X"
- Never fabricate facts from training data
- Suggest creating a memory entry if appropriate

## Example: Person Profile

```markdown
---
summary: "Alice Chen - Senior engineer, prefers TypeScript, works on backend APIs"
created: 2026-01-15
updated: 2026-02-20
tags: [people, engineering, backend]
related: [projects/api-v2.md]
---

# Alice Chen

## Role
Senior Backend Engineer

## Preferences
- Language: TypeScript over JavaScript
- Testing: Jest with high coverage
- Code style: Functional programming patterns

## Projects
- API v2 redesign (lead)
- Authentication service (contributor)

## Communication
- Prefers async communication (Slack)
- Available 9am-6pm PST
- Responds to urgent issues within 1 hour
```

## Example: Daily Log

```markdown
---
summary: "2026-02-24 - Fixed memory leak, deployed API v2, team meeting"
created: 2026-02-24
tags: [daily, deployment, bug-fix]
---

# 2026-02-24

## Events
- 10:00 - Fixed memory leak in worker threads ([related: mistakes.md#worker-leak])
- 14:00 - Deployed API v2 to production ([related: projects/api-v2.md])
- 16:00 - Team retrospective meeting

## Decisions
- Agreed to use TypeScript for all new services
- Set up weekly memory cleanup task

## Notes
- Alice mentioned preference for functional patterns
- Need to document deployment process
```

## Best Practices

1. **Write for resumption**: Include enough context to continue work later without losing state
2. **Keep summaries decisive**: Reading the summary should tell you if you need the full content
3. **Stay current**: Update or delete outdated information regularly
4. **Be practical**: Save what's useful, not everything
5. **Link related content**: Use `related:` field to connect information

## Why File-Based?

- **LLM-friendly**: Plain text, easy to read and write
- **Version control**: Git-compatible for tracking changes
- **Portable**: No database dependencies
- **Inspectable**: Humans can read and edit directly
- **Efficient**: Summary-first search minimizes token usage

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.
