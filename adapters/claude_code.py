"""Claude Code adaptor — uses the generic rule+skill+hooks installer.

The ai-act-audit-log skill ships SKILL.md documenting when and how to call
log_event from builtin_tools.audit. The AgentskillsAdaptor installs it on the
Claude Code harness. No scripts/ re-export is needed here — builtin_tools.audit
does not use @tool-decorated functions; the audit layer is passive (other
tools call log_event to emit events, it does not itself expose agent-callable tools).
"""
from plugins_registry.builtins import AgentskillsAdaptor as Adaptor  # noqa: F401
