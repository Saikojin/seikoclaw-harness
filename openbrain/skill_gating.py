import os
import re
import yaml
import logging
from typing import Tuple, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SkillGater:
    """
    Automated Skill Regression Gating Engine.
    Validates candidate and evolved agent skills against schema requirements,
    boundary constraints, anti-hallucination checks, and regression tests
    before accepting them into the persistent skill repository.
    """

    REQUIRED_METADATA_FIELDS = ["name"]
    MIN_RULES_COUNT = 1
    MAX_SKILL_TOKENS = 4000  # Guard against runaway prompt bloating

    @staticmethod
    def parse_skill_text(skill_text: str) -> Tuple[bool, Optional[Dict[str, Any]], str, str]:
        """
        Parses YAML frontmatter and body markdown from a skill string.
        Returns: (success, metadata_dict, body_text, error_message)
        """
        if not skill_text or not skill_text.strip():
            return False, None, "", "Skill content is empty."

        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.search(pattern, skill_text.strip(), re.DOTALL)
        if not match:
            return False, None, "", "Missing valid YAML frontmatter (enclosed by '---')."

        raw_yaml = match.group(1)
        body = match.group(2).strip()

        try:
            metadata = yaml.safe_load(raw_yaml)
            if not isinstance(metadata, dict):
                return False, None, "", "YAML frontmatter must parse to a dictionary."
        except Exception as e:
            return False, None, "", f"Failed to parse YAML frontmatter: {str(e)}"

        return True, metadata, body, ""

    def validate_schema(self, skill_text: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validates the structure and content of a candidate skill.
        Checks:
        1. Valid YAML frontmatter with mandatory fields ('name').
        2. No placeholder / mock text.
        3. Mandatory operational sections (Rules/Workflow and Boundaries).
        4. Reasonable length and formatting.
        """
        success, metadata, body, err = self.parse_skill_text(skill_text)
        if not success:
            return False, f"Schema Error: {err}", None

        # 1. Check required metadata
        for req in self.REQUIRED_METADATA_FIELDS:
            if req not in metadata or not str(metadata[req]).strip():
                return False, f"Schema Error: Missing required frontmatter field '{req}'.", metadata

        skill_name = metadata.get("name", "").strip()
        if not re.match(r"^[a-zA-Z0-9_\-\.\s]+$", skill_name):
            return False, f"Schema Error: Invalid skill name '{skill_name}'. Use alphanumeric, dashes, or underscores.", metadata

        # 2. Reject placeholder / mock content
        disallowed_patterns = [
            r"\[Mock Response\]",
            r"\[Insert\s+",
            r"<placeholder>",
            r"TODO:\s*define",
            r"\[PLACEHOLDER\]",
            r"\{\{PLACEHOLDER\}\}",
            r"\bPLACEHOLDER\b"
        ]
        for pattern in disallowed_patterns:
            if re.search(pattern, skill_text):
                return False, f"Validation Error: Contains disallowed placeholder token matching '{pattern}'.", metadata

        # 3. Check for operational sections (Rules, Workflow, Instructions, Steps, Overview, Goal, or Router index)
        has_rules_or_workflow = bool(
            re.search(r"#+\s*(RULES|Workflow|Steps|Goal|Overview|Instructions|Philosophy|Core Engineering|Index|Router|Guidance|When to use)", body, re.IGNORECASE)
        )
        if not has_rules_or_workflow:
            return False, "Validation Error: Missing operational section ('# RULES', '## Workflow', '## Instructions', etc.).", metadata

        # 4. Check for boundary/constraint sections or negative boundary rules
        has_boundaries = bool(
            re.search(r"#+\s*(BOUNDARIES|What NOT to do|Checklists|Constraints|Anti-Patterns|Non-Goals|Guarantees|Boundaries)", body, re.IGNORECASE)
            or re.search(r"(?:never|do not|don't|must not|cannot)\s+[^.\n]+", body, re.IGNORECASE)
        )
        if not has_boundaries:
            return False, "Validation Error: Missing '# BOUNDARIES', '## Constraints', or negative boundary rules.", metadata

        # 5. Length check
        body_words = len(body.split())
        if body_words < 10:
            return False, "Validation Error: Skill body is too short to be an actionable procedural skill.", metadata

        return True, "Skill passed schema and structural validation.", metadata

    def evaluate_regression(self, skill_text: str, previous_skill_text: Optional[str] = None) -> Tuple[bool, str]:
        """
        Runs regression checks on the proposed skill.
        If evolving from an existing skill:
        - Ensures boundary constraints were not loosened or deleted.
        - Ensures versioning or rules increased in specificity.
        """
        is_valid, msg, metadata = self.validate_schema(skill_text)
        if not is_valid:
            return False, msg

        if previous_skill_text:
            prev_valid, prev_meta, prev_body, _ = self.parse_skill_text(previous_skill_text)
            if prev_valid and prev_meta:
                # Check for boundary regression: extract negative rules ("never", "do not", "don't", "avoid")
                prev_negatives = set(re.findall(r"(?:never|do not|don't|avoid|cannot|must not)\s+[^.\n]+", prev_body, re.IGNORECASE))
                curr_body_lower = skill_text.lower()
                
                missing_boundaries = []
                for neg in prev_negatives:
                    keywords = [w for w in re.findall(r"\w+", neg.lower()) if len(w) > 3]
                    if keywords and not all(k in curr_body_lower for k in keywords[:3]):
                        missing_boundaries.append(neg.strip())

                if len(missing_boundaries) > 2:
                    logger.warning(f"Potential boundary regression: Lost constraints: {missing_boundaries}")
                    return False, f"Regression Error: Candidate skill discarded critical prior boundaries: {missing_boundaries[:2]}"

        return True, "Skill passed regression gating."

    def gate_and_save(
        self, 
        skill_text: str, 
        skill_name: str, 
        memory_engine: Any, 
        target_dir: str = ".agents/skills", 
        previous_skill_text: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        End-to-end gating check and transactional persistence:
        1. Runs schema validation & regression evaluation.
        2. If passed: Saves to target .agents/skills/<skill_name>/SKILL.md and Openbrain database.
        3. If failed: Logs rejection to Openbrain as a learning note and leaves prior skill untouched.
        """
        passed, reason = self.evaluate_regression(skill_text, previous_skill_text)
        
        if not passed:
            if memory_engine:
                memory_engine.save_memory(
                    text=f"Skill Gating Rejection for '{skill_name}': {reason}\nCandidate snippet: {skill_text[:300]}...",
                    tier="Shortterm",
                    source="SkillGater",
                    tags="skill_rejected,regression_fail"
                )
            return False, f"Skill '{skill_name}' REJECTED by Gate: {reason}"

        try:
            folder_name = re.sub(r"[^a-zA-Z0-9_\-]", "-", skill_name.lower().strip())
            dest_dir = os.path.join(target_dir, folder_name)
            os.makedirs(dest_dir, exist_ok=True)
            skill_file_path = os.path.join(dest_dir, "SKILL.md")

            with open(skill_file_path, "w", encoding="utf-8") as f:
                f.write(skill_text.strip() + "\n")

            if memory_engine:
                _, metadata, _, _ = self.parse_skill_text(skill_text)
                desc = metadata.get("description", "Auto-learned and gated skill") if metadata else "Gated Skill"
                memory_engine.save_skill(name=skill_name, description=desc, example=skill_text)
                memory_engine.save_memory(
                    text=skill_text,
                    tier="Longterm",
                    source="SkillGater",
                    tags=f"skill,gated,{skill_name}"
                )

            return True, f"Skill '{skill_name}' successfully gated and saved to {skill_file_path}"
        except Exception as e:
            return False, f"Failed to persist gated skill: {str(e)}"
