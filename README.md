# molecule-audit

EU AI Act compliance audit log (Articles 12/13/17). Immutable append-only JSON Lines format, SIEM-friendly, write-only. Usually paired with `molecule-compliance`.

## What it logs

Records for every AI system operation:
- Timestamp, actor, action, outcome
- Input/output data categories
- Human oversight actions
- System failure events

Format: JSON Lines (`.jsonl`) — one record per line, no envelope.

## How it works

`builtin_tools/audit.py` provides the log writer. This plugin is the opt-in policy layer that activates it per workspace.

## Install

### In org template (org.yaml)

```yaml
plugins:
  - molecule-audit
```

**Recommended sibling:** `molecule-compliance` for complete coverage.

### From URL (community install)

```
github://Molecule-AI/molecule-ai-plugin-molecule-audit
```

## Configuration

```yaml
audit:
  log_path: .claude/ai-act-audit.jsonl
  retention_days: 365
  siem_endpoint: https://your-siem.example.com/ingest
```

## Runtimes

- `langgraph` — primary
- `claude_code` — supported
- `deepagents` — supported

## Skills

- `ai-act-audit-log` — agent guidance on AI Act article requirements

## Architecture

```
skills/
  ai-act-audit-log/
    SKILL.md   # Agent-side guidance (when/how to call log_event)
adapters/
  claude_code.py  # Installs skill via AgentskillsAdaptor; no scripts/ needed —
                  # builtin_tools.audit does not expose @tool-decorated functions;
                  # the audit layer is passive (other tools call log_event)
```

## Known issues

See [known-issues.md](known-issues.md).

## License

Business Source License 1.1 — © Molecule AI.
