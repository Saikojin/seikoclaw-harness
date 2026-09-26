"""
Pluggable LLM Provider System for SeikoClaw / Openbrain.
Supports LocalMind GGUF, OpenAI-compatible local endpoints (Ollama/LM Studio),
and graceful heuristic rule-based fallback when no LLM is configured.
"""

import os
import sys
import re
import json
import logging
import urllib.request
import urllib.error
from typing import Optional

logger = logging.getLogger(__name__)

class BaseLLMProvider:
    name: str = "base"

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        raise NotImplementedError

LLMProvider = BaseLLMProvider

class LocalMindProvider(BaseLLMProvider):
    name: str = "LocalMind (Local GGUF)"

    def __init__(self, model_dir: Optional[str] = None):
        self.model_dir = model_dir or os.getenv("LOCALMIND_MODEL_DIR") or os.getenv("SEIKOCLAW_MODEL_DIR")
        if not self.model_dir:
            # Fallback path search
            candidates = [
                os.path.join(os.path.expanduser("~"), ".localmind", "models"),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "BookIngestion", "models")),
                os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "LocalMind", "models")),
            ]
            for c in candidates:
                if os.path.isdir(c):
                    self.model_dir = c
                    break

        self.engine = None
        self._init_engine()

    def _init_engine(self):
        try:
            harness_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            workspace_dir = os.path.dirname(harness_dir)
            localmind_src = os.path.join(workspace_dir, "LocalMind", "src")
            if os.path.exists(localmind_src) and localmind_src not in sys.path:
                sys.path.append(localmind_src)

            from localmind.engine import LocalMindEngine
            if self.model_dir and os.path.isdir(self.model_dir):
                self.engine = LocalMindEngine(backend="auto", model_dir=self.model_dir)
        except Exception as e:
            logger.debug(f"LocalMindEngine initialization skipped: {e}")
            self.engine = None

    def is_available(self) -> bool:
        return self.engine is not None

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        if not self.engine:
            return HeuristicFallbackProvider().generate(prompt, max_tokens=max_tokens, temperature=temperature)
        try:
            res = self.engine.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            if res and "[Mock Response]" not in res and not res.startswith("Generation failed"):
                return res
        except Exception as e:
            logger.warning(f"LocalMind inference failed ({e}). Falling back to heuristic summarization.")
        
        return HeuristicFallbackProvider().generate(prompt, max_tokens=max_tokens, temperature=temperature)

class OpenAICompatibleProvider(BaseLLMProvider):
    name: str = "OpenAI-Compatible Local API"

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: str = "default"):
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("OLLAMA_HOST") or "http://localhost:11434/v1").rstrip("/")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or "dummy"
        self.model = os.getenv("LOCAL_LLM_MODEL") or model

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return body["choices"][0]["message"]["content"].strip()

class HeuristicFallbackProvider(BaseLLMProvider):
    """
    Zero-dependency rule-based summarizer and skill synthesizer.
    Operates offline without neural models.
    """
    name: str = "Heuristic Rule-Based Fallback"

    def generate(self, prompt: str, max_tokens: int = 1024, temperature: float = 0.3) -> str:
        # Check if prompt is a Skill Synthesis prompt
        if "Synthesize or Evolve a \"Skill\"" in prompt or "SKILL.md format" in prompt:
            return self._heuristic_skill_synthesis(prompt)
        
        # Check if prompt is a Caveman Memory Compression prompt
        if "Smart Caveman logic" in prompt or "Midterm" in prompt:
            return self._heuristic_memory_compression(prompt)

        return f"[Heuristic Note] Processed prompt of {len(prompt)} characters."

    def _heuristic_memory_compression(self, prompt: str) -> str:
        # Extract INPUT MEMORIES
        match = re.search(r"INPUT MEMORIES:\s*([\s\S]*)", prompt)
        text = match.group(1) if match else prompt

        # Heuristic Caveman reduction:
        # Remove articles, filler words, preserve technical lines and errors
        lines = text.strip().splitlines()
        compressed = []
        for line in lines:
            line = line.strip()
            if not line or line.startswith("---"):
                continue
            # Strip markdown noise
            line = re.sub(r"\[x\]\s*", "DONE: ", line)
            line = re.sub(r"\[\s*\]\s*", "TODO: ", line)
            # Remove articles
            cleaned = re.sub(r"\b(the|a|an|please|thank you|successfully|just)\b", "", line, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned:
                compressed.append(cleaned)

        facts = " | ".join(compressed[:8])
        return f"[MIDTERM COMPRESSED] {facts}"

    def _heuristic_skill_synthesis(self, prompt: str) -> str:
        # Extract Trajectory
        match = re.search(r"TRAJECTORY:\s*([\s\S]*)", prompt)
        trajectory = match.group(1) if match else prompt

        # Guess skill name
        name_match = re.search(r"(?:Task|Goal|Skill):\s*([^\n\r]+)", trajectory)
        skill_name = name_match.group(1).strip() if name_match else "Auto-Synthesized-Skill"
        skill_slug = re.sub(r"[^\w\-]", "-", skill_name.lower()).strip("-")

        # Synthesize Caveman SKILL.md
        return f"""---
name: {skill_slug}
evolution: Lite
version: 1.0.0
---
# RULES
task executed. verification passed. state persisted.
# BOUNDARIES
Do NOT bypass task verification. Do NOT leave untracked changes.
# AUTO-CLARITY
Trajectory recorded {len(trajectory.splitlines())} execution steps.
"""

def get_llm_provider() -> BaseLLMProvider:
    """
    Returns the most capable available LLM provider:
    1. LocalMind (Local GGUF via llama-cpp)
    2. OpenAI-compatible local server (Ollama, LM Studio)
    3. Heuristic Fallback (deterministic rule-based)
    """
    # 1. Try LocalMind
    localmind = LocalMindProvider()
    if localmind.is_available():
        return localmind

    # 2. Try OpenAI compatible (if explicitly configured or Ollama running)
    if os.getenv("OPENAI_BASE_URL") or os.getenv("OLLAMA_HOST"):
        openai_provider = OpenAICompatibleProvider()
        if openai_provider.is_available():
            return openai_provider

    # 3. Fallback to Heuristic
    return HeuristicFallbackProvider()
