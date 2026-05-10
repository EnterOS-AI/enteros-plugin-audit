# Test Coverage Rationale — molecule-audit

## Why This Plugin Has Limited Unit-Test Coverage

`molecule-audit` is a **skill-only plugin** — it provides EU AI Act audit log
policy documentation via prose SKILL.md and a `known-issues.md`. The JSON Lines
log writer (`audit.log_event`) lives in `builtin_tools/audit.py` in molecule-core
and is tested there.

## What We Test (and Why)

| What | Why |
|------|-----|
| `plugin.yaml` schema | Verifies name, semver version, description, runtimes, skill registration |
| `ai-act-audit-log` SKILL.md | Frontmatter parses, event schema fields present, when-to-install, configuration, SIEM ingestion, anti-patterns, builtin_tools reference |
| `known-issues.md` | Active Issues + Reporting + Severity Definitions sections present |
| `README.md` | H1 heading, Install section, Configuration section |

## What We Cannot Unit-Test Here

- **SKILL.md prose content** — EU AI Act article coverage and event schema prose
  quality are a compliance review concern.

- **Audit log writer** — `log_event` and the JSON Lines formatter are tested in
  molecule-core's `builtin_tools/audit.py` test suite.

## Integration Tests

If you want to test the full audit pipeline end-to-end:
1. Install `molecule-audit` on a test workspace
2. Trigger a delegation or approval action
3. Verify a JSON line appears in the configured `log_path`
4. Verify SIEM ingestion if `siem_endpoint` is configured
