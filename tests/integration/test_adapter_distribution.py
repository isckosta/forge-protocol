from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_SCHEMAS = (
    "adapter.schema.json",
    "adapter-installation.schema.json",
)


def _build_wheel(tmp_path: Path) -> Path:
    wheel_dir = tmp_path / "wheel"
    wheel_dir.mkdir()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(REPOSITORY_ROOT),
            "--no-deps",
            "--wheel-dir",
            str(wheel_dir),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )

    wheels = tuple(wheel_dir.glob("forge_protocol-*.whl"))
    assert len(wheels) == 1
    return wheels[0]


def test_adapter_schemas_are_packaged_and_resolvable_without_source_tree(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    extracted = tmp_path / "installed"

    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(extracted)
        names = set(archive.namelist())

    for schema_name in ADAPTER_SCHEMAS:
        packaged_path = f"forge_cli/resources/protocol/schemas/{schema_name}"
        assert packaged_path in names

    probe = """
import json
from pathlib import Path
import forge_cli
from forge_cli.protocol_resources import resolve_protocol_root

root = resolve_protocol_root()
assert Path(forge_cli.__file__).resolve().is_relative_to(Path({extracted!r}).resolve())
for name in {schemas!r}:
    path = root / 'schemas' / name
    assert path.is_file(), path
    json.loads(path.read_text(encoding='utf-8'))
""".format(extracted=str(extracted), schemas=ADAPTER_SCHEMAS)

    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(extracted)
    environment["PYTHONNOUSERSITE"] = "1"
    environment["PIP_NO_INDEX"] = "1"

    subprocess.run(
        [sys.executable, "-c", probe],
        cwd=tmp_path,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
