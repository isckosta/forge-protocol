from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import venv
import zipfile

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


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


def _run(command: list[str], *, cwd: Path, environment: dict[str, str]) -> None:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise AssertionError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )


def test_adapter_schemas_are_packaged_and_resolvable_without_source_tree(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    extracted = tmp_path / "installed"

    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(extracted)
        names = set(archive.namelist())
        catalog_path = "forge_cli/resources/protocol/schemas/catalog.yml"
        assert catalog_path in names
        catalog = yaml.safe_load(archive.read(catalog_path))
    cataloged_files = {entry["file"] for entry in catalog["schemas"]}
    packaged_schema_files = {
        Path(name).name
        for name in names
        if name.startswith("forge_cli/resources/protocol/schemas/")
        and name.endswith(".schema.json")
    }
    assert packaged_schema_files == cataloged_files

    probe = """
import json
from pathlib import Path
import forge_cli
import yaml
from jsonschema import Draft202012Validator
from forge_cli.protocol_resources import resolve_protocol_root

root = resolve_protocol_root()
assert Path(forge_cli.__file__).resolve().is_relative_to(Path({extracted!r}).resolve())
catalog_path = root / 'schemas' / 'catalog.yml'
catalog = yaml.safe_load(catalog_path.read_text(encoding='utf-8'))
catalog_schema = json.loads((root / 'schemas' / 'schema-catalog.schema.json').read_text(encoding='utf-8'))
Draft202012Validator.check_schema(catalog_schema)
Draft202012Validator(catalog_schema).validate(catalog)
cataloged = {{entry['file'] for entry in catalog['schemas']}}
packaged = {{path.name for path in (root / 'schemas').glob('*.schema.json')}}
assert packaged == cataloged
for entry in catalog['schemas']:
    path = root / 'schemas' / entry['file']
    assert path.is_file(), path
    schema = json.loads(path.read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    assert schema['properties']['schema']['const'] == entry['id']
""".format(extracted=str(extracted))

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


def test_installed_wheel_runs_the_codex_adapter_golden_path_offline(tmp_path: Path) -> None:
    wheelhouse = tmp_path / "wheelhouse"
    wheelhouse.mkdir()
    build_environment = os.environ.copy()
    build_environment.pop("PYTHONPATH", None)
    build_environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    _run(
        [
            sys.executable,
            "-m",
            "pip",
            "wheel",
            str(REPOSITORY_ROOT),
            "--wheel-dir",
            str(wheelhouse),
        ],
        cwd=tmp_path,
        environment=build_environment,
    )
    wheels = tuple(wheelhouse.glob("forge_protocol-*.whl"))
    assert len(wheels) == 1

    environment_root = tmp_path / "installed-venv"
    venv.EnvBuilder(with_pip=True).create(environment_root)
    executable_directory = environment_root / ("Scripts" if os.name == "nt" else "bin")
    installed_python = executable_directory / ("python.exe" if os.name == "nt" else "python")
    forge = executable_directory / ("forge.exe" if os.name == "nt" else "forge")
    install_environment = os.environ.copy()
    install_environment.pop("PYTHONPATH", None)
    install_environment["PIP_NO_INDEX"] = "1"
    install_environment["PIP_DISABLE_PIP_VERSION_CHECK"] = "1"
    install_environment["PIP_CONFIG_FILE"] = os.devnull
    _run(
        [
            str(installed_python),
            "-m",
            "pip",
            "install",
            "--no-index",
            "--find-links",
            str(wheelhouse),
            "forge-protocol",
        ],
        cwd=tmp_path,
        environment=install_environment,
    )
    assert forge.is_file()

    repository = tmp_path / "repository"
    repository.mkdir()
    _run(["git", "init", str(repository)], cwd=tmp_path, environment=install_environment)
    probe = Path(__file__).with_name("adapter_cli_wheel_probe.py")
    runtime_environment = install_environment.copy()
    runtime_environment.pop("VIRTUAL_ENV", None)
    runtime_environment["PYTHONNOUSERSITE"] = "1"
    _run(
        [str(installed_python), str(probe), str(forge), str(repository)],
        cwd=tmp_path,
        environment=runtime_environment,
    )
