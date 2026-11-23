#!/usr/bin/env python3
"""Atomically reserve the next change-unit id for this Git repository."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path


UNIT_DIR_PATTERN = re.compile(r"^(?:feat|bugfix|refactor|perf|docs|chore)-(\d+)(?:-|$)")
CHANGE_TYPES = ("feat", "bugfix", "refactor", "perf", "docs", "chore")


def existing_numbers(changes_dir: Path) -> set[int]:
    """Collect unit numbers from active, archived, and retired unit directories."""
    numbers: set[int] = set()
    for parent in (
        changes_dir,
        changes_dir / "archive",
        changes_dir / "retired",
    ):
        if not parent.is_dir():
            continue
        for child in parent.iterdir():
            if not child.is_dir():
                continue
            match = UNIT_DIR_PATTERN.match(child.name)
            if match:
                numbers.add(int(match.group(1)))
    return numbers


def git_common_dir(changes_dir: Path) -> Path:
    """Return the shared Git directory used by every worktree in this clone."""
    result = subprocess.run(
        [
            "git",
            "-C",
            str(changes_dir),
            "rev-parse",
            "--path-format=absolute",
            "--git-common-dir",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or "not inside a Git repository"
        raise ValueError(message)
    return Path(result.stdout.strip())


def read_last_reservation(counter_path: Path) -> int:
    """Read the largest locally reserved number, tolerating a fresh state dir."""
    if not counter_path.exists():
        return 0
    value = counter_path.read_text(encoding="utf-8").strip()
    if not value.isdecimal():
        raise ValueError(f"invalid reservation state: {counter_path}")
    return int(value)


def write_last_reservation(counter_path: Path, number: int) -> None:
    """Replace reservation state atomically while the allocation lock is held."""
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=counter_path.parent,
        prefix=f".{counter_path.name}.",
        delete=False,
    ) as temporary:
        temporary.write(f"{number}\n")
        temporary.flush()
        os.fsync(temporary.fileno())
        temporary_path = Path(temporary.name)
    os.replace(temporary_path, counter_path)


@contextmanager
def allocation_lock(path: Path):
    """Serialize reservations across worktrees and allocator processes."""
    with path.open("a+b") as lock:
        if os.name == "nt":
            import msvcrt

            if lock.seek(0, os.SEEK_END) == 0:
                lock.write(b"0")
                lock.flush()
            lock.seek(0)
            msvcrt.locking(lock.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl

            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        # Both operating systems release this lock when the handle closes.
        yield


def reserve_next_number(changes_dir: Path, state_dir: Path) -> int:
    """Reserve a unique number across concurrent processes and worktrees."""
    state_dir.mkdir(parents=True, exist_ok=True)
    lock_path = state_dir / "allocation.lock"
    counter_path = state_dir / "last-number"

    with allocation_lock(lock_path):
        last_reserved = read_last_reservation(counter_path)
        next_number = (
            max(max(existing_numbers(changes_dir), default=0), last_reserved) + 1
        )
        write_last_reservation(counter_path, next_number)
        return next_number


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Allocate the next global docs/changes unit id."
    )
    parser.add_argument("change_type", choices=CHANGE_TYPES)
    parser.add_argument(
        "--changes-dir",
        type=Path,
        default=None,
        help="Path to docs/changes (default: docs/changes).",
    )
    parser.add_argument(
        "--state-dir",
        type=Path,
        help=(
            "Shared reservation state directory. Defaults to "
            "the clone's shared Git directory."
        ),
    )
    args = parser.parse_args()

    try:
        if args.changes_dir is None:
            root = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()
            args.changes_dir = Path(root) / "docs" / "changes"
        args.changes_dir.mkdir(parents=True, exist_ok=True)
        if args.state_dir is None:
            shared = git_common_dir(args.changes_dir)
            # Older project worktrees can allocate concurrently in a fresh clone.
            # Use their on-disk namespace even before it has been created.
            args.state_dir = shared / "nano-multiagent" / "change-unit-ids"
        next_number = reserve_next_number(args.changes_dir, args.state_dir)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    print(f"{args.change_type}-{next_number}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
