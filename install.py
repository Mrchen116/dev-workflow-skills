#!/usr/bin/env python3
"""Register skills from this checkout for local coding agents."""

import argparse
from pathlib import Path


def install(source: Path, destinations: list[Path]) -> None:
    """Link this checkout's skills, preserving unrelated user entries."""
    skills = sorted(file.parent for file in source.glob("*/SKILL.md"))
    if not skills:
        raise ValueError(f"No skills in {source}")
    pending = {}
    conflicts = []
    stale = set()
    for directory in {path.resolve() for path in destinations}:
        if directory.is_dir():
            for entry in directory.iterdir():
                previous = source / entry.name
                if (
                    entry.is_symlink()
                    and entry.readlink() == previous
                    and previous not in skills
                ):
                    stale.add(entry)
        for skill in skills:
            target = directory.resolve() / skill.name
            if target.is_symlink() and target.resolve() == skill.resolve():
                continue
            if target.is_symlink() or target.exists():
                conflicts.append(str(target))
            else:
                pending[target] = skill.resolve()
    if conflicts:
        raise ValueError("Existing skill entries conflict:\n" + "\n".join(conflicts))
    for target, skill in pending.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(skill, target_is_directory=True)
    for entry in stale:
        entry.unlink()
    print(
        f"Registered {len(skills)} skills ({len(pending)} new, {len(stale)} obsolete links removed)."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        choices=("codex", "claude"),
        action="append",
        help="Register with this local agent (default: both).",
    )
    args = parser.parse_args()
    directories = {
        "codex": Path.home() / ".agents/skills",
        "claude": Path.home() / ".claude/skills",
    }
    try:
        install(
            Path(__file__).resolve().parent / "skills",
            [directories[name] for name in (args.target or directories)],
        )
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
