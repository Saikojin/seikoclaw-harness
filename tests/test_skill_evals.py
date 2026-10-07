"""
Unit tests for SeikoClaw Skill Routing & Collision Evaluation Engine.
"""

import os
import json
import pytest
from pathlib import Path
from scripts.eval_skill_routing import (
    load_all_skills,
    detect_collisions,
    route_query,
    run_eval_cases,
    tokenize,
    parse_skill_file
)


@pytest.fixture
def repo_root():
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def skills_dir(repo_root):
    return repo_root / ".agents" / "skills"


@pytest.fixture
def routing_cases_file(repo_root):
    return repo_root / "evals" / "routing" / "routing_cases.json"


def test_tokenization():
    tokens = tokenize("Decompose this high-level goal into a task checklist")
    assert "decompose" in tokens
    assert "goal" in tokens
    assert "checklist" in tokens
    # Stop words like 'this', 'a', 'into' should be filtered
    assert "this" not in tokens
    assert "into" not in tokens


def test_load_all_skills(skills_dir):
    skills, lint_errors = load_all_skills(str(skills_dir))
    assert len(skills) >= 60, f"Expected at least 60 canonical skills, found {len(skills)}"
    assert len(lint_errors) == 0, f"Expected 0 frontmatter lint errors, found: {lint_errors}"
    assert "architect" in skills
    assert "tdd" in skills
    assert "deslop" in skills
    assert "seikojin-qa" in skills
    assert "obsidian-cli" in skills
    assert "obsidian-markdown" in skills
    assert "json-canvas" in skills
    assert "obsidian-bases" in skills
    assert "obsidian-atlas-vtt" in skills


def test_detect_no_vocabulary_collisions(skills_dir):
    skills, _ = load_all_skills(str(skills_dir))
    collisions = detect_collisions(skills, threshold=0.65)
    assert len(collisions) == 0, f"Detected vocabulary collisions: {collisions}"


def test_route_query_precision(skills_dir):
    skills, _ = load_all_skills(str(skills_dir))

    # Test distinct queries
    queries = [
        ("Remove AI-generated slop and clean up code style", "deslop"),
        ("Follow test-driven development red-green-refactor", "tdd"),
        ("Stress-test this architecture and find blind spots", "interrogate"),
        ("Seikojin QA agent cabinet risk based testing", "seikojin-qa"),
        ("Cut game design scope to a testable vertical micro-slice", "scope-surgeon"),
        ("Interact with Obsidian vaults using the Obsidian CLI", "obsidian-cli"),
        ("Author valid Obsidian Flavored Markdown with wikilinks and callouts", "obsidian-markdown"),
        ("Author JSON Canvas flowcharts with nodes and edges", "json-canvas"),
        ("Create Obsidian Bases database views with filters and formulas", "obsidian-bases"),
        ("Atlas VTT virtual tabletop scene creation and uvtt imports in Obsidian", "obsidian-atlas-vtt"),
    ]

    for query, expected in queries:
        ranked = route_query(skills, query, top_k=3)
        assert len(ranked) > 0, f"No matches found for '{query}'"
        top_skill = ranked[0][0]
        assert top_skill == expected, f"Query '{query}' expected '{expected}', got '{top_skill}' (top 3: {ranked})"


def test_canonical_routing_cases(skills_dir, routing_cases_file):
    assert routing_cases_file.exists(), f"Cases file not found at {routing_cases_file}"
    skills, _ = load_all_skills(str(skills_dir))
    eval_result = run_eval_cases(skills, str(routing_cases_file))

    assert eval_result["total"] >= 30, f"Expected at least 30 test cases, got {eval_result['total']}"
    assert eval_result["failed"] == 0, f"Failed cases: {[r for r in eval_result['results'] if not r['passed']]}"
    assert eval_result["accuracy"] == 100.0
