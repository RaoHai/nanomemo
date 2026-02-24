---
summary: "Memory system index - structured archive directory, core principles, tag ontology"
updated: 2026-02-24
---

# Memory Index

Structured memory system following SSOT (Single Source of Truth) principles.

## Core Principles

1. **Single Source of Truth (SSOT)**: Each entity's facts exist in exactly one canonical file
2. **Related Links**: Cross-file references use `related:` field
3. **Tag System**: Use `tags:` field for cross-domain search
4. **Search First**: When uncertain, search; if not found, admit it
5. **Proactive Sniffing**: Automatically fetch entity profiles when mentioned

## Tag Ontology

**Technical**: `ai-agents` `memory-systems` `benchmarks` `web-dev` `frontend` `infra` `llm`

**People**: `people` `team` `family` `ai-agent` `friend`

**Content**: `content-creation` `project` `events` `daily`

## Archive Directory

| Path | Content |
|------|---------|
| `people/` | Person profiles and relationships |
| `projects/` | Project information and status |
| `events/` | Important events and milestones |
| `credentials/` | Sensitive credentials and API keys |
| `infra/` | Infrastructure configurations |
| `daily/YYYY-MM-DD.md` | Daily event logs |
| `mistakes.md` | Error log and lessons learned |
| `tools/preferences.md` | Tool preferences and settings |

## Memory Operations SOP

### 1. Write Rules
- **Trigger**: New facts, state changes, configuration updates, or lessons learned
- **Action**:
  1. Identify or create the entity's canonical file (prefer categorized directories)
  2. Update `related:` field in frontmatter if new associations emerge
  3. Append brief entry to `daily/YYYY-MM-DD.md` with entity link
- **Conflict Resolution**: When `daily/` conflicts with canonical file, latest timestamp wins
- **⚠️ MEMORY.md Write Restriction**: **Never** write entity data or events to this file. Only modify the "Archive Directory" table (add/remove rows). All content must go to subdirectory files.

### 2. Proactive Search SOP
Don't wait for explicit user commands. **Must** proactively search when:
- **Entity appears**: Person, project, system, or work mentioned → fetch canonical file
- **Ambiguous reference**: "he/she/it", "that bug" → search `daily/` or related files
- **Preference check**: Before generating solutions → check entity preferences
- **Hallucination prevention**: When search returns empty → say "no memory found", **never** fabricate from training data

### 3. Frontmatter Format
```yaml
---
summary: "One-line entity description or event summary with key entities"
created: 2026-02-24
updated: 2026-02-24  # Optional
status: in-progress  # Optional: in-progress | resolved | blocked | abandoned
tags: [tag1, tag2]   # Optional
related: [path/to/related.md]  # Optional
---
```

## Search Workflow

```bash
# 1. List categories
ls memory/

# 2. View all summaries
rg "^summary:" memory/ --no-ignore --hidden

# 3. Search summaries by keyword
rg "^summary:.*keyword" memory/ --no-ignore --hidden -i

# 4. Search by tag
rg "^tags:.*keyword" memory/ --no-ignore --hidden -i

# 5. Full-text search
rg "keyword" memory/ --no-ignore --hidden -i

# 6. Read specific file
cat memory/path/to/file.md
```

**Note**: Memory files are gitignored, use `--no-ignore --hidden` flags.

## Guidelines

1. **Write for resumption**: Capture all context needed to continue work later
2. **Keep summaries decisive**: Summary should tell you if you need full content
3. **Stay current**: Update or delete outdated information
4. **Be practical**: Save what's useful, not everything
5. **Link related content**: Use `related:` field to connect information
