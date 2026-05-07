# Local Development Setup

This runbook covers setting up a local development environment for
`molecule-audit`.

---

## Prerequisites

- Python 3.11+
- `gh` CLI authenticated
- Write access to `Molecule-AI/molecule-ai-plugin-molecule-audit`

---

## Clone & Bootstrap

```bash
git clone https://git.moleculesai.app/molecule-ai/molecule-ai-plugin-molecule-audit.git
cd molecule-ai-plugin-molecule-audit
```

---

## Validating Plugin Structure

```bash
# YAML structure validation
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
echo "plugin.yaml OK"

# Check all referenced skill paths exist
python3 -c "
import yaml, os
with open('plugin.yaml') as f:
    data = yaml.safe_load(f)
for skill in data.get('skills', []):
    path = f'skills/{skill}/SKILL.md'
    exists = os.path.exists(path)
    print(f'[{\"OK\" if exists else \"MISSING\"}] {path}')
"
```

---

## Testing the Audit Skill Locally

The `builtin_tools/audit.py` harness wrapper is not in this repo — it is
provided by the Molecule AI platform at runtime. To test the skill locally:

1. **Install the plugin in a test workspace** via the platform UI or
   `molecule-cli`:
   ```bash
   mol workspace plugin install molecule-audit --workspace <test-wsid>
   ```

2. **Trigger a delegation** in the test workspace and check the log file:
   ```bash
   cat /path/to/workspace/audit/ai-act-log.jsonl | jq .
   ```

3. **Validate JSONL integrity**:
   ```bash
   # Check each line is valid JSON
   while IFS= read -r line; do
     echo "$line" | python3 -c "import json,sys; json.load(sys.stdin)" 2>/dev/null \
       || echo "INVALID: $line"
   done < /path/to/ai-act-log.jsonl
   echo "Integrity check complete"
   ```

---

## Simulating a SIEM Export

To verify your SIEM config is correct without a live SIEM:

```bash
# Generate a sample log line
python3 -c "
import json, uuid, datetime
event = {
    'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    'event_type': 'delegation',
    'workspace_id': str(uuid.uuid4()),
    'actor': 'test-agent',
    'action': 'delegate_task',
    'resource': 'ws-target',
    'outcome': 'pass',
    'trace_id': str(uuid.uuid4()),
    'detail': {'task': 'test', 'async': False}
}
print(json.dumps(event))
" > /tmp/test-audit.jsonl

# Verify Splunk/ELK-compatible parsing
python3 -c "
import json
with open('/tmp/test-audit.jsonl') as f:
    for i, line in enumerate(f):
        obj = json.loads(line)
        assert 'timestamp' in obj
        assert 'event_type' in obj
        assert 'outcome' in obj
        print(f'Line {i}: OK — {obj[\"event_type\"]}')
"
```

---

## Troubleshooting

### plugin.yaml fails to load

```bash
python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"
# If this throws, your YAML is malformed
```

### Audit log file not created

- Ensure `audit.enabled: true` is set in workspace `config.yaml`
- Check the workspace has write access to the `log_path` directory
- The harness must be providing `builtin_tools/audit.py` — verify
  the platform version includes it

### JSONL is corrupted (one line fails to parse)

This usually means two workspaces are writing to the same `log_path`.
The append-only stream was opened for writing by more than one process.
Fix: assign each workspace a unique log path.

### SIEM shows no events after ingestion

- Confirm the Filebeat/Agent tail is reading the right path
- Check the SIEM has permission to read the log file
- Verify the JSON fields match the SIEM field-mapping config

---

## Related

- `builtin_tools/audit.py` — the platform-provided audit implementation
- `molecule-compliance` — runtime OWASP policy companion
- `skills/ai-act-audit-log/SKILL.md` — full skill documentation
