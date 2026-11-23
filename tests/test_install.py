import importlib.util
from pathlib import Path

import pytest


def test_register_editable_links_and_preserve_conflicts(tmp_path):
    spec = importlib.util.spec_from_file_location(
        "installer", Path(__file__).resolve().parents[1] / "install.py"
    )
    installer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(installer)
    source = tmp_path / "source"
    skill = source / "example"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("first")
    dest = tmp_path / "registry"
    other = tmp_path / "occupied"
    (other / "example").mkdir(parents=True)
    with pytest.raises(ValueError, match="Existing"):
        installer.install(source, [dest, other])
    assert not dest.exists()
    installer.install(source, [dest])
    installer.install(source, [dest, dest])
    (skill / "SKILL.md").write_text("changed")
    assert (dest / "example/SKILL.md").read_text() == "changed"

    skill.rename(source / "renamed")
    external = dest / "external"
    external.symlink_to(tmp_path / "another-checkout")
    installer.install(source, [dest])
    assert not (dest / "example").is_symlink()
    assert (dest / "renamed").resolve() == source / "renamed"
    assert external.is_symlink()
