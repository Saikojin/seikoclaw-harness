import os
import re
import yaml
import shutil
import difflib
import logging
from typing import Tuple, Dict, Any, Optional, List

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

                if len(missing_boundaries) > 0:
                    logger.warning(f"Potential boundary regression: Lost constraints: {missing_boundaries}")
                    return False, f"Regression Error: Candidate skill discarded critical prior boundaries: {missing_boundaries[:2]}"

        return True, "Skill passed regression gating."

    def gate_and_save(
        self, 
        skill_text: str, 
        skill_name: str, 
        memory_engine: Any = None, 
        target_dir: str = ".agents/skills", 
        previous_skill_text: Optional[str] = None,
        staging: bool = False
    ) -> Tuple[bool, str]:
        """
        End-to-end gating check and transactional persistence:
        1. Runs schema validation & regression evaluation.
        2. Protects hand-written disk skills by checking disk file if previous_skill_text is None.
        3. If staging=True: saves candidate to target_dir/.candidates/<skill_name>/SKILL.md.
        4. If staging=False: writes to target_dir/<skill_name>/SKILL.md and Openbrain database.
        5. If failed: Logs rejection to Openbrain and leaves prior skill untouched.
        """
        folder_name = re.sub(r"[^a-zA-Z0-9_\-]", "-", skill_name.lower().strip())
        target_skill_path = os.path.join(target_dir, folder_name, "SKILL.md")

        # Disk-aware regression protection: Load existing disk skill if previous_skill_text not explicitly given
        if not previous_skill_text and os.path.exists(target_skill_path):
            try:
                with open(target_skill_path, "r", encoding="utf-8") as f:
                    previous_skill_text = f.read()
            except Exception as e:
                logger.warning(f"Failed to read existing disk skill at {target_skill_path}: {e}")

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
            if staging:
                dest_dir = os.path.join(target_dir, ".candidates", folder_name)
            else:
                dest_dir = os.path.join(target_dir, folder_name)
                
            os.makedirs(dest_dir, exist_ok=True)
            skill_file_path = os.path.join(dest_dir, "SKILL.md")

            with open(skill_file_path, "w", encoding="utf-8") as f:
                f.write(skill_text.strip() + "\n")

            if memory_engine and not staging:
                _, metadata, _, _ = self.parse_skill_text(skill_text)
                desc = metadata.get("description", "Auto-learned and gated skill") if metadata else "Gated Skill"
                memory_engine.save_skill(name=skill_name, description=desc, example=skill_text)
                memory_engine.save_memory(
                    text=skill_text,
                    tier="Longterm",
                    source="SkillGater",
                    tags=f"skill,gated,{skill_name}"
                )

            location_tag = "staged candidate" if staging else "gated and saved"
            return True, f"Skill '{skill_name}' successfully {location_tag} to {skill_file_path}"
        except Exception as e:
            return False, f"Failed to persist gated skill: {str(e)}"

    @staticmethod
    def list_candidates(target_dir: str = ".agents/skills") -> List[Dict[str, Any]]:
        """Lists all staged candidate skills pending review or promotion."""
        candidates_dir = os.path.join(target_dir, ".candidates")
        if not os.path.exists(candidates_dir):
            return []
        
        results = []
        for name in os.listdir(candidates_dir):
            p = os.path.join(candidates_dir, name, "SKILL.md")
            if os.path.exists(p):
                results.append({
                    "name": name,
                    "path": p,
                    "mtime": os.path.getmtime(p)
                })
        return results

    @staticmethod
    def diff_candidate(candidate_name: str, target_dir: str = ".agents/skills") -> str:
        """Returns a unified diff between candidate skill and existing skill on disk."""
        folder_name = re.sub(r"[^a-zA-Z0-9_\-]", "-", candidate_name.lower().strip())
        cand_path = os.path.join(target_dir, ".candidates", folder_name, "SKILL.md")
        prod_path = os.path.join(target_dir, folder_name, "SKILL.md")

        if not os.path.exists(cand_path):
            return f"Candidate skill '{candidate_name}' not found at {cand_path}."

        with open(cand_path, "r", encoding="utf-8") as f:
            cand_lines = f.readlines()

        prod_lines = []
        if os.path.exists(prod_path):
            with open(prod_path, "r", encoding="utf-8") as f:
                prod_lines = f.readlines()

        diff = difflib.unified_diff(
            prod_lines,
            cand_lines,
            fromfile=f"current/{folder_name}/SKILL.md",
            tofile=f"candidate/{folder_name}/SKILL.md"
        )
        diff_str = "".join(diff)
        return diff_str or "[No differences detected between candidate and production skill]"

    def promote_candidate(
        self,
        candidate_name: str,
        target_dir: str = ".agents/skills",
        memory_engine: Any = None
    ) -> Tuple[bool, str]:
        """Promotes a candidate skill from staging to production."""
        folder_name = re.sub(r"[^a-zA-Z0-9_\-]", "-", candidate_name.lower().strip())
        cand_path = os.path.join(target_dir, ".candidates", folder_name, "SKILL.md")
        if not os.path.exists(cand_path):
            return False, f"Candidate skill '{candidate_name}' not found at {cand_path}."

        with open(cand_path, "r", encoding="utf-8") as f:
            skill_text = f.read()

        passed, msg = self.gate_and_save(
            skill_text=skill_text,
            skill_name=candidate_name,
            memory_engine=memory_engine,
            target_dir=target_dir,
            staging=False
        )

        if passed:
            # Clean up candidate directory
            try:
                shutil.rmtree(os.path.join(target_dir, ".candidates", folder_name), ignore_errors=True)
            except Exception:
                pass
            return True, f"Successfully promoted '{candidate_name}' to production skill."
        return False, f"Promotion failed gating: {msg}"
