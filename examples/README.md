# Example Memory Structure

This directory demonstrates a typical NanoMemo setup.

```
memory/
├── MEMORY.md              # Index (copy from templates/)
├── people/
│   ├── alice.md          # Person profile
│   └── bob.md
├── projects/
│   ├── api-v2.md         # Project info
│   └── mobile-app.md
├── events/
│   └── 2026-02-team-offsite.md
├── daily/
│   ├── 2026-02-20.md     # Daily logs
│   ├── 2026-02-21.md
│   └── 2026-02-24.md
├── credentials/
│   └── api-keys.md       # Sensitive info
├── infra/
│   └── production.md     # Infrastructure configs
├── mistakes.md           # Error log
└── tools/
    └── preferences.md    # Tool preferences
```

## Quick Start

1. Copy `templates/MEMORY.md` to your `memory/` directory
2. Create subdirectories as needed
3. Use templates for consistent formatting
4. Search with ripgrep: `rg "^summary:" memory/ --no-ignore --hidden`
