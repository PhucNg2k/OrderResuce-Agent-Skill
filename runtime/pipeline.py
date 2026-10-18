"""Fixed-order pipeline runner.

The order below is the agent's flow. It is code, not a model choice: the model
never decides which skill runs next, and the gates can never be skipped.
"""
from __future__ import annotations

import importlib.util
import re
from functools import lru_cache
from pathlib import Path
from types import ModuleType

from runtime.models import PipelineState

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"

PIPELINE = [
    "load-case",               # gate 1: can this case still be assessed?
    "build-evidence",          # snapshot of what is known at the virtual "now"
    "assess-case",             # the only AI step
    "validate-output",         # check the AI output against evidence + confidence rules
    "policy-gate",             # gate 2: is the next step allowed right now?
    "compose-recommendation",  # approved wording for the decision card
    "audit-log",               # append-only decision history
]


def read_frontmatter(skill_md: Path) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", skill_md.read_text(encoding="utf-8"), re.S)
    if not match:
        return {}
    pairs = (line.split(":", 1) for line in match.group(1).splitlines() if ":" in line)
    return {k.strip(): v.strip() for k, v in pairs}


@lru_cache(maxsize=None)
def load_skill(name: str) -> ModuleType:
    folder = SKILLS_DIR / name
    meta = read_frontmatter(folder / "SKILL.md")
    if meta.get("name") != name:
        raise RuntimeError(f"skills/{name}/SKILL.md must declare name: {name}")
    spec = importlib.util.spec_from_file_location(f"skills.{name.replace('-', '_')}", folder / "skill.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_pipeline(state: PipelineState) -> PipelineState:
    for name in PIPELINE:
        skill = load_skill(name)
        if state.halted and not getattr(skill, "RUNS_WHEN_HALTED", False):
            continue
        state = skill.run(state)
        state.trace.append(name)
    return state
