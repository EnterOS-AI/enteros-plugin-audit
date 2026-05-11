#!/usr/bin/env python3
"""
Smoke tests for molecule-audit.

Rationale: This is a skill-only plugin. The audit log implementation
lives in builtin_tools/audit.py in molecule-core. This plugin contributes
the policy layer and documentation. Smoke tests verify all artifacts exist
and parse correctly. See tests/README.md.

Run: python tests/test_audit_smoke.py
"""
import os
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestPluginManifest(unittest.TestCase):
    """Verify plugin.yaml is well-formed."""

    @classmethod
    def setUpClass(cls):
        import yaml
        manifest_path = os.path.join(REPO_ROOT, 'plugin.yaml')
        with open(manifest_path) as f:
            cls.manifest = yaml.safe_load(f)

    def test_plugin_yaml_loads(self):
        self.assertIsInstance(self.manifest, dict)

    def test_name(self):
        self.assertEqual(self.manifest['name'], 'molecule-audit')

    def test_version_semver(self):
        import re
        v = self.manifest['version']
        self.assertRegex(v, r'^\d+\.\d+\.\d+$', f"Version {v!r} not semver")

    def test_description_present(self):
        self.assertGreater(len(self.manifest.get('description', '')), 10)

    def test_runtimes_include_claude_code(self):
        self.assertIn('claude_code', self.manifest.get('runtimes', []))

    def test_skill_declared(self):
        skills = self.manifest.get('skills', [])
        self.assertIn('ai-act-audit-log', skills)


class TestAiActAuditLogSkill(unittest.TestCase):
    """Verify ai-act-audit-log skill exists and documents EU AI Act coverage."""

    SKILL_PATH = os.path.join(REPO_ROOT, 'skills', 'ai-act-audit-log', 'SKILL.md')

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.SKILL_PATH))

    def test_has_frontmatter(self):
        import yaml
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertTrue(content.startswith('---'))
        parts = content.split('---', 2)
        self.assertEqual(len(parts), 3)
        _, frontmatter, _ = parts
        data = yaml.safe_load(frontmatter)
        self.assertIsInstance(data, dict)

    def test_frontmatter_name(self):
        import yaml
        with open(self.SKILL_PATH) as f:
            content = f.read()
        parts = content.split('---', 2)
        _, frontmatter, body = parts
        data = yaml.safe_load(frontmatter)
        self.assertEqual(data['name'], 'ai-act-audit-log')

    def test_body_has_event_schema(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('event_type', content)
        self.assertIn('timestamp', content)
        self.assertIn('trace_id', content)

    def test_body_has_when_to_install_section(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('When to install', content)

    def test_body_has_configuration_section(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('config.yaml', content)
        self.assertIn('log_path:', content)

    def test_body_has_siem_ingestion(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('SIEM', content)

    def test_body_has_anti_patterns(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('Anti-patterns', content)

    def test_body_references_builtin_tools(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('builtin_tools', content)

    def test_body_references_compliance_plugin(self):
        with open(self.SKILL_PATH) as f:
            content = f.read()
        self.assertIn('molecule-compliance', content)


class TestKnownIssues(unittest.TestCase):
    """Verify known-issues.md structure."""

    KI_PATH = os.path.join(REPO_ROOT, 'known-issues.md')

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.KI_PATH))

    def test_has_active_issues_section(self):
        with open(self.KI_PATH) as f:
            self.assertIn('Active Issues', f.read())

    def test_has_reporting_section(self):
        with open(self.KI_PATH) as f:
            content = f.read()
        self.assertIn('Reporting', content)

    def test_has_severity_definitions(self):
        with open(self.KI_PATH) as f:
            content = f.read()
        self.assertIn('Severity Definitions', content)


class TestReadme(unittest.TestCase):
    """Verify README.md has required sections."""

    README_PATH = os.path.join(REPO_ROOT, 'README.md')

    def test_readme_exists(self):
        self.assertTrue(os.path.isfile(self.README_PATH))

    def test_readme_has_h1(self):
        with open(self.README_PATH) as f:
            first_line = f.readline().strip()
        self.assertTrue(
            first_line.startswith('# '),
            f"README must start with # heading, got: {first_line!r}"
        )

    def test_readme_has_install_section(self):
        with open(self.README_PATH) as f:
            content = f.read()
        self.assertIn('Install', content)

    def test_readme_has_configuration_section(self):
        with open(self.README_PATH) as f:
            content = f.read()
        self.assertIn('config', content.lower())


class TestClaudeCodeAdaptor(unittest.TestCase):
    """Verify the claude_code runtime adapter is present and well-formed."""

    ADAPTER_PATH = os.path.join(REPO_ROOT, 'adapters', 'claude_code.py')
    SKILL_PATH = os.path.join(REPO_ROOT, 'skills', 'ai-act-audit-log', 'SKILL.md')

    def test_adapter_file_exists(self):
        self.assertTrue(os.path.isfile(self.ADAPTER_PATH))

    def test_adapter_exports_adaptor(self):
        with open(self.ADAPTER_PATH) as f:
            content = f.read()
        self.assertIn('Adaptor', content)

    def test_skill_md_has_runtime_field(self):
        """SKILL.md frontmatter declares runtime:[claude_code] so the skill
        loader does not skip this skill for the Claude Code runtime."""
        import yaml
        with open(self.SKILL_PATH) as f:
            content = f.read()
        parts = content.split('---', 2)
        _, frontmatter, _ = parts
        data = yaml.safe_load(frontmatter)
        self.assertIn('runtime', data)


class TestValidatePlugin(unittest.TestCase):
    """Smoke-test validate-plugin.py."""

    def test_exits_zero(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, os.path.join(REPO_ROOT, '.molecule-ci', 'scripts', 'validate-plugin.py')],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, f"stdout: {result.stdout}\nstderr: {result.stderr}")
        self.assertIn('molecule-audit', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
