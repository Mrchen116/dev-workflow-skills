import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pr_templates_use_stable_absolute_blob_links():
    template = ROOT / "skills/change-orchestrator/references/pr-body-templates.md"
    targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", template.read_text())
    unit_links = [target for target in targets if "<unit_dir>" in target]
    assert unit_links
    assert all(
        target.startswith("<repo_url>/blob/<pr_head_sha>/") for target in unit_links
    )
