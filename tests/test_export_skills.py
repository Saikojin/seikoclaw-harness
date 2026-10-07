"""
Unit tests for Cross-Harness Skill Exporter & External Importer.
"""

import os
import pytest
from pathlib import Path
from scripts.export_skills import export_skills, import_skills


@pytest.fixture
def mock_skills_env(tmp_path):
    source_dir = tmp_path / "source_skills"
    source_dir.mkdir()

    # Create dummy skill A
    skill_a = source_dir / "perf-audit"
    skill_a.mkdir()
    (skill_a / "SKILL.md").write_text("---\nname: perf-audit\ndescription: Audit web performance and vitals\n---\n# Perf\n", encoding="utf-8")

    # Create dummy skill B
    skill_b = source_dir / "a11y-check"
    skill_b.mkdir()
    (skill_b / "SKILL.md").write_text("---\nname: a11y-check\ndescription: Check WCAG accessibility compliance\n---\n# A11y\n", encoding="utf-8")

    return source_dir, tmp_path


def test_export_skills(mock_skills_env):
    source_dir, tmp_path = mock_skills_env
    target_dir = tmp_path / "exported"

    count = export_skills(str(source_dir), str(target_dir))
    assert count == 2
    assert (target_dir / "perf-audit" / "SKILL.md").exists()
    assert (target_dir / "a11y-check" / "SKILL.md").exists()


def test_import_skills_with_namespace(mock_skills_env):
    source_dir, tmp_path = mock_skills_env
    canonical_skills_dir = tmp_path / "canonical_skills"
    canonical_skills_dir.mkdir()

    # Import with namespace 'addy'
    count = import_skills(str(source_dir), str(canonical_skills_dir), namespace="addy")
    assert count == 2

    namespaced_a = canonical_skills_dir / "addy-perf-audit"
    assert namespaced_a.exists()
    skill_content = (namespaced_a / "SKILL.md").read_text(encoding="utf-8")
    assert "name: addy-perf-audit" in skill_content

    namespaced_b = canonical_skills_dir / "addy-a11y-check"
    assert namespaced_b.exists()
    skill_b_content = (namespaced_b / "SKILL.md").read_text(encoding="utf-8")
    assert "name: addy-a11y-check" in skill_b_content


def test_import_skills_skip_existing_without_overwrite(mock_skills_env):
    source_dir, tmp_path = mock_skills_env
    target_dir = tmp_path / "imported"

    count1 = import_skills(str(source_dir), str(target_dir))
    assert count1 == 2

    # Second import without overwrite should skip
    count2 = import_skills(str(source_dir), str(target_dir), overwrite=False)
    assert count2 == 0
