"""
Tier 2 Skill Routing & Collision Evaluation Engine for SeikoClaw.
Validates skill frontmatter, detects description/vocabulary collisions across skills,
and evaluates natural language utterance routing against canonical test suites.
"""

import os
import sys
import re
import json
import math
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import yaml

# Fix for Windows terminal UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Standard stop words for tokenization
STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "aren't", "as", "at", "be", "because", "been", "before", "being", "below", "between", "both",
    "but", "by", "can", "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't",
    "doing", "don't", "down", "during", "each", "few", "for", "from", "further", "had", "hadn't",
    "has", "hasn't", "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i", "i'd", "i'll",
    "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", "its", "itself", "let's",
    "me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of", "off", "on", "once",
    "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there",
    "there's", "these", "they", "they'd", "they'll", "they're", "they've", "this", "those",
    "through", "to", "too", "under", "until", "up", "very", "was", "wasn't", "we", "we'd",
    "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", "where",
    "where's", "which", "while", "who", "who's", "whom", "with", "won't",
    "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves", "guides", "agent", "agents"
}


def tokenize(text: str) -> List[str]:
    """Tokenize text into lowercase alphanumeric words, stripping punctuation and stop words."""
    if not text:
        return []
    words = re.findall(r'[a-zA-Z0-9_\-]+', text.lower())
    clean_words = []
    for w in words:
        # Split on hyphens as well to capture sub-tokens
        sub = w.replace("_", "-").split("-")
        for s in sub:
            if len(s) > 1 and s not in STOP_WORDS:
                clean_words.append(s)
        if len(w) > 1 and w not in STOP_WORDS:
            clean_words.append(w)
    return clean_words


def parse_skill_file(skill_path: Path) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Parses a SKILL.md file, extracting frontmatter and returning any lint errors."""
    errors = []
    try:
        content = skill_path.read_text(encoding="utf-8-sig")
    except Exception as e:
        return None, [f"Failed to read file: {e}"]

    # Normalize line endings
    content = content.replace("\r\n", "\n")

    # Match YAML frontmatter between --- and ---
    match = re.match(r"^---\s*\n(.*?)\n---\s*(?:\n|$)(.*)$", content, re.DOTALL)
    if not match:
        return None, ["Missing YAML frontmatter delimiters ('---')"]

    frontmatter_raw = match.group(1)
    body = match.group(2)

    try:
        data = yaml.safe_load(frontmatter_raw)
    except yaml.YAMLError as e:
        return None, [f"Invalid YAML in frontmatter: {e}"]

    if not isinstance(data, dict):
        return None, ["Frontmatter is not a valid YAML dictionary mapping"]

    name = data.get("name")
    description = data.get("description")

    if not name or not isinstance(name, str):
        errors.append("Missing or invalid 'name' field in frontmatter")
    else:
        name = name.strip()
        dir_name = skill_path.parent.name
        # Allow slight variation if prefixed or alias, but flag obvious mismatches
        if name != dir_name and not dir_name.endswith(name) and not name.endswith(dir_name):
            errors.append(f"Skill name '{name}' does not match directory '{dir_name}'")

    if not description or not isinstance(description, str):
        errors.append("Missing or invalid 'description' field in frontmatter")
    elif len(description.strip()) < 15:
        errors.append(f"Description is too short ({len(description.strip())} chars; min 15)")

    return {
        "name": name or skill_path.parent.name,
        "description": description or "",
        "author": data.get("author", "Unknown"),
        "triggers": data.get("triggers", []),
        "path": str(skill_path),
        "dir": skill_path.parent.name,
        "body_preview": body[:200]
    }, errors


def load_all_skills(skills_dir: str, include_candidates: bool = False) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, List[str]]]:
    """Scans skills directory and loads all SKILL.md definitions."""
    base_path = Path(skills_dir).resolve()
    skills = {}
    lint_results = {}

    if not base_path.exists():
        return skills, {str(base_path): ["Directory does not exist"]}

    for item in sorted(base_path.iterdir()):
        if not item.is_dir():
            continue
        if item.name.startswith(".") and not (include_candidates and item.name == ".candidates"):
            continue

        skill_file = item / "SKILL.md"
        if not skill_file.exists():
            continue

        skill_data, errors = parse_skill_file(skill_file)
        if errors:
            lint_results[item.name] = errors
        if skill_data:
            skills[skill_data["name"]] = skill_data

    return skills, lint_results


def compute_token_frequencies(skills: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    """Computes document frequency for tokens across all skill descriptions."""
    df = {}
    for s in skills.values():
        tokens = set(tokenize(f"{s['name']} {s['description']} {' '.join(s.get('triggers', []))}"))
        for t in tokens:
            df[t] = df.get(t, 0) + 1
    return df


def score_skill_against_query(skill: Dict[str, Any], raw_query: str, query_tokens: List[str], df: Dict[str, int], total_docs: int) -> float:
    """Scores a skill against query tokens using TF-IDF weighted overlap and name matching."""
    text = f"{skill['name']} {skill['description']} {' '.join(skill.get('triggers', []))}"
    skill_tokens = tokenize(text)
    token_counts = {}
    for t in skill_tokens:
        token_counts[t] = token_counts.get(t, 0) + 1

    score = 0.0
    skill_name_lower = skill["name"].lower()
    raw_query_lower = raw_query.lower()

    # Exact name or trigger whole-word boost
    if re.search(rf"\b{re.escape(skill_name_lower)}\b", raw_query_lower):
        score += 25.0
    for trigger in skill.get("triggers", []):
        if re.search(rf"\b{re.escape(trigger.lower())}\b", raw_query_lower):
            score += 20.0

    for q in query_tokens:
        if q in token_counts:
            # Term frequency
            tf = 1 + math.log(token_counts[q])
            # Inverse document frequency
            doc_freq = df.get(q, 1)
            idf = math.log((total_docs + 1) / (doc_freq + 0.5))
            weight = tf * idf

            # Name match gets extra weight
            if q in skill_name_lower:
                weight *= 3.0

            score += weight

    return score


def detect_collisions(skills: Dict[str, Dict[str, Any]], threshold: float = 0.65) -> List[Dict[str, Any]]:
    """Detects pairs of skills with excessively high description overlap (potential routing collisions)."""
    collisions = []
    skill_names = sorted(list(skills.keys()))

    token_sets = {}
    for name in skill_names:
        s = skills[name]
        tokens = set(tokenize(f"{s['description']}"))
        token_sets[name] = tokens

    for i in range(len(skill_names)):
        name_a = skill_names[i]
        set_a = token_sets[name_a]
        if not set_a:
            continue

        for j in range(i + 1, len(skill_names)):
            name_b = skill_names[j]
            set_b = token_sets[name_b]
            if not set_b:
                continue

            # Jaccard similarity of description tokens
            intersection = len(set_a.intersection(set_b))
            union = len(set_a.union(set_b))
            jaccard = intersection / union if union > 0 else 0.0

            if jaccard >= threshold:
                shared = sorted(list(set_a.intersection(set_b)))
                collisions.append({
                    "skill_a": name_a,
                    "skill_b": name_b,
                    "similarity": round(jaccard, 3),
                    "shared_tokens": shared[:10]
                })

    return collisions


def route_query(skills: Dict[str, Dict[str, Any]], query: str, top_k: int = 3) -> List[Tuple[str, float]]:
    """Ranks skills for a given user query."""
    tokens = tokenize(query)
    if not tokens:
        return []

    df = compute_token_frequencies(skills)
    total_docs = len(skills)
    scores = []

    for name, skill in skills.items():
        s = score_skill_against_query(skill, query, tokens, df, total_docs)
        if s > 0:
            scores.append((name, round(s, 2)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:top_k]


def run_eval_cases(skills: Dict[str, Dict[str, Any]], cases_path: str) -> Dict[str, Any]:
    """Runs a benchmark routing test cases JSON file against the loaded skills catalog."""
    p = Path(cases_path).resolve()
    if not p.exists():
        return {"error": f"Cases file not found: {p}", "total": 0, "passed": 0, "failed": 0, "accuracy": 0.0}

    with open(p, "r", encoding="utf-8") as f:
        cases = json.load(f)

    total = len(cases)
    passed = 0
    results = []

    for case in cases:
        query = case.get("query", "")
        expected = case.get("expected", "")
        ranked = route_query(skills, query, top_k=5)

        top_1 = ranked[0][0] if ranked else None
        top_names = [r[0] for r in ranked]

        is_top1 = (top_1 == expected)
        in_top3 = (expected in top_names[:3])

        if is_top1:
            passed += 1

        results.append({
            "query": query,
            "expected": expected,
            "top_1": top_1,
            "top_candidates": top_names[:3],
            "passed": is_top1,
            "in_top3": in_top3
        })

    accuracy = (passed / total) * 100.0 if total > 0 else 0.0
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "accuracy": round(accuracy, 1),
        "results": results
    }


def main():
    parser = argparse.ArgumentParser(description="Tier 2 Skill Routing & Collision Evaluation Engine")
    parser.add_argument("--skills-dir", type=str, default=".agents/skills", help="Path to skills directory")
    parser.add_argument("--check-lint", action="store_true", help="Run YAML frontmatter schema linter")
    parser.add_argument("--detect-collisions", action="store_true", help="Detect description vocabulary collisions")
    parser.add_argument("--collision-threshold", type=float, default=0.65, help="Jaccard similarity threshold for collision detection")
    parser.add_argument("--query", type=str, help="Route a single query and print top skill matches")
    parser.add_argument("--cases", type=str, help="Run routing benchmark test cases JSON file")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    args = parser.parse_args()

    skills, lint_errors = load_all_skills(args.skills_dir)
    has_errors = False
    output = {}

    if args.check_lint:
        output["lint"] = {
            "total_skills": len(skills),
            "errors": lint_errors,
            "passed": len(lint_errors) == 0
        }
        if not args.json:
            print(f"=== 🔍 Skill Frontmatter Linter ({len(skills)} skills loaded) ===")
            if lint_errors:
                print(f"[FAIL] Found {len(lint_errors)} skills with lint errors:")
                for s_name, errs in lint_errors.items():
                    print(f"  - {s_name}: {', '.join(errs)}")
                has_errors = True
            else:
                print(f"[OK] All {len(skills)} skills have valid frontmatter (name, description).")

    if args.detect_collisions:
        collisions = detect_collisions(skills, threshold=args.collision_threshold)
        output["collisions"] = {
            "threshold": args.collision_threshold,
            "count": len(collisions),
            "collisions": collisions
        }
        if not args.json:
            print(f"\n=== ⚠️ Skill Collision Detection (Threshold: {args.collision_threshold}) ===")
            if collisions:
                print(f"[WARN] Found {len(collisions)} potential collision pairs:")
                for c in collisions:
                    print(f"  - {c['skill_a']} <-> {c['skill_b']} (sim: {c['similarity']}) [shared: {', '.join(c['shared_tokens'][:5])}]")
            else:
                print(f"[OK] No vocabulary collisions detected above threshold {args.collision_threshold}.")

    if args.query:
        matches = route_query(skills, args.query, top_k=5)
        output["query"] = {
            "input": args.query,
            "matches": matches
        }
        if not args.json:
            print(f"\n=== 🎯 Query Routing: '{args.query}' ===")
            for rank, (name, sc) in enumerate(matches, 1):
                print(f"  {rank}. {name} (score: {sc})")

    if args.cases:
        eval_res = run_eval_cases(skills, args.cases)
        output["eval"] = eval_res
        if not args.json:
            print(f"\n=== 📊 Benchmark Routing Evaluation ({eval_res['total']} cases) ===")
            print(f"Passed: {eval_res['passed']}/{eval_res['total']} ({eval_res['accuracy']}%)")
            if eval_res["failed"] > 0:
                print(f"[FAIL] Failed cases:")
                for r in eval_res["results"]:
                    if not r["passed"]:
                        print(f"  - Query: \"{r['query']}\"")
                        print(f"    Expected: {r['expected']} | Got: {r['top_1']} (Candidates: {', '.join(r['top_candidates'])})")
                has_errors = True
            else:
                print(f"[OK] 100% of test utterances correctly routed!")

    if args.json:
        print(json.dumps(output, indent=2))

    if has_errors:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
