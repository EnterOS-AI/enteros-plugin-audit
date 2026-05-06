# molecule-audit — EU AI Act Audit Log

`molecule-audit` is an **immutable append-only JSON Lines (JSONL) audit log**
plugin for EU AI Act compliance (Articles 12/13/17). It wraps
`builtin_tools/audit.py` and is SIEM-friendly, write-only, and opt-in per
workspace.

**Version:** 1.0.0
**Runtime:** `langgraph`, `claude_code`, `deepagents`
**Usually paired with:** `molecule-compliance` (runtime OWASP policy)

---

## Repository Layout

```
molecule-audit/
├── plugin.yaml              — Plugin manifest
├── skills/
│   └── ai-act-audit-log/
│       └── SKILL.md         — Full skill documentation
└── builtin_tools/           — (harness-provided, not in this repo)
    └── audit.py             — Audit log implementation
```

---

## What Gets Logged

Events are written to a JSONL file (one JSON object per line):

| Field | Type | Description |
|---|---|---|
| `timestamp` | ISO 8601 | Event time |
| `event_type` | string | Delegation, approval, RBAC, memory_read, memory_write |
| `workspace_id` | UUID | Workspace that generated the event |
| `actor` | string | Agent or user who triggered the action |
| `action` | string | What was done |
| `resource` | string | Target of the action |
| `outcome` | string | pass / deny / error |
| `trace_id` | string | Platform trace correlation ID |
| `detail` | object | Event-specific extra fields |

### Event Types

- **Delegation** — A2A task delegation between workspaces
- **Approval** — Human-in-the-loop gate approval or rejection
- **RBAC** — Role-based access control decision
- **memory_read** — Agent read from persistent memory
- **memory_write** — Agent wrote to persistent memory

### Anti-Patterns (never do these)

- Do not write from multiple workspaces to the same log path — this
  corrupts the JSONL stream and makes it unreadable.
- Do not truncate logs with `>` instead of `>>` — destroys the append-only
  guarantee.
- Do not log raw PII. Scrub tokens, emails, and workspace IDs from
  `detail` fields before emission.
- Do not skip OA-01 (bias audit) or OA-03 (explainability) detections.

---

## Configuration

In workspace `config.yaml`:

```yaml
audit:
  enabled: true
  log_path: /workspace/audit/ai-act-log.jsonl
  max_size_mb: 100
  retention_days: 90
```

| Setting | Default | Description |
|---|---|---|
| `enabled` | `false` | Opt-in — audit is off by default |
| `log_path` | — | Required when enabled |
| `max_size_mb` | `100` | Rotate when file exceeds this |
| `retention_days` | `90` | Days to retain before archiving |

---

## Log Rotation

The plugin writes append-only. Use **external logrotate with `copytruncate`**
to avoid breaking the write stream:

```
/path/to/ai-act-log.jsonl {
  daily
  rotate 14
  compress
  copytruncate
  missingok
  notifempty
}
```

**Never use `truncate` or `size 0`** — that destroys unwritten buffered events.

---

## SIEM Integration

The JSONL format is compatible with:

| SIEM | Ingestion |
|---|---|
| Splunk | `source = /path/to/ai-act-log.jsonl` |
| Elastic (ELK) | Filebeat with `json` codec |
| Datadog | `dd-agent` JSON log files |
| Grafana Loki | `json` label parser |

---

## Development

### Prerequisites

- Node.js >= 18 (for markdownlint, if editing `.md` files)
- Python 3.11+ (for YAML validation)
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-audit`

### Setup

```bash
git clone https://github.com/Molecule-AI/molecule-ai-plugin-molecule-audit.git
cd molecule-ai-plugin-molecule-audit

# Validate plugin.yaml
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
```

### Pre-Commit Checklist

```bash
# YAML structure
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"

# Markdown lint (if any .md edited)
npx markdownlint '**/*.md' --ignore node_modules 2>/dev/null || true

# No credentials in plugin.yaml
python3 -c "
import re, sys
with open('plugin.yaml') as f:
    content = f.read()
patterns = [r'sk.ant', r'ghp.', r'AKIA[A-Z0-9]']
if any(re.search(p, content) for p in patterns):
    print('FAIL: possible credentials found')
    sys.exit(1)
print('No credentials: OK')
"
```

---

## Release Process

1. Review changes: `git log origin/main..HEAD --oneline`
2. Bump `version` in `plugin.yaml` (semver)
3. Update `**Version:**` in this CLAUDE.md if conventions changed
4. Commit: `chore: bump version to X.Y.Z`
5. Tag and push: `git tag vX.Y.Z && git push origin main --tags`
6. Create GitHub Release with changelog

---

## Adding a New Event Type

1. Define the event schema in `skills/ai-act-audit-log/SKILL.md`
2. Add it to the Event Types table above
3. Ensure `builtin_tools/audit.py` handles the new type (harness-level change)
4. Update SIEM ingestion configs if field structure changes

---

## Known Issues

See `known-issues.md` at the repo root.
