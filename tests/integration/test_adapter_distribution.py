from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import venv
import zipfile

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

_RUNTIME_ENVIRONMENT_KEYS = {
    "FORGE_WHEEL_GUARD_MARKER",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_NOSYSTEM",
    "GIT_TERMINAL_PROMPT",
    "HOME",
    "LANG",
    "LC_ALL",
    "PATH",
    "PIP_CONFIG_FILE",
    "PIP_DISABLE_PIP_VERSION_CHECK",
    "PIP_NO_INDEX",
    "PYTHONNOUSERSITE",
    "TMPDIR",
    "XDG_CONFIG_HOME",
}

_NETWORK_GUARD = """
import os
from pathlib import Path
import socket
import sys

_MESSAGE = "network disabled by installed-wheel verification guard"

def _deny(*_args, **_kwargs):
    raise RuntimeError(_MESSAGE)

socket.socket.connect = _deny
socket.socket.connect_ex = _deny
socket.create_connection = _deny
socket.getaddrinfo = _deny

def _audit(event, _args):
    if event.startswith("socket."):
        raise RuntimeError(_MESSAGE)

sys.addaudithook(_audit)

if marker := os.environ.get("FORGE_WHEEL_GUARD_MARKER"):
    Path(marker).write_text("loaded\\n", encoding="utf-8")
""".lstrip()


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


def _run(
    command: list[str], *, cwd: Path, environment: dict[str, str]
) -> subprocess.CompletedProcess[str]:
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
    return completed


def _isolated_runtime_environment(tmp_path: Path) -> dict[str, str]:
    home = tmp_path / "runtime-home"
    temp_directory = tmp_path / "runtime-tmp"
    config_directory = home / "config"
    for directory in (home, temp_directory, config_directory):
        directory.mkdir(parents=True, exist_ok=True)
    environment = {
        "PATH": os.environ["PATH"],
        "HOME": str(home),
        "TMPDIR": str(temp_directory),
        "XDG_CONFIG_HOME": str(config_directory),
        "LANG": os.environ.get("LANG", "C.UTF-8"),
        "LC_ALL": os.environ.get("LC_ALL", "C.UTF-8"),
        "PYTHONNOUSERSITE": "1",
        "PIP_NO_INDEX": "1",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "PIP_CONFIG_FILE": os.devnull,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "FORGE_WHEEL_GUARD_MARKER": str(temp_directory / "sitecustomize-loaded"),
    }
    assert set(environment) == _RUNTIME_ENVIRONMENT_KEYS
    assert not any(
        "proxy" in key.lower() or "credential" in key.lower() or "token" in key.lower()
        for key in environment
    )
    return environment


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
    expected_wheel_contents = tmp_path / "expected-wheel-contents"
    with zipfile.ZipFile(wheels[0]) as archive:
        archive.extractall(expected_wheel_contents)
    expected_protocol = expected_wheel_contents / "forge_cli" / "resources" / "protocol"
    assert (expected_protocol / "contract" / "engineering.md").is_file()
    expected_effective_flows = tmp_path / "expected-effective-flows"
    expected_effective_flows.mkdir()
    for flow in (expected_protocol / "flows").glob("*.yml"):
        expected_effective_flows.joinpath(flow.name).write_text(
            yaml.safe_dump(
                yaml.safe_load(flow.read_text(encoding="utf-8")),
                sort_keys=False,
                allow_unicode=True,
            ),
            encoding="utf-8",
        )

    environment_root = tmp_path / "installed-venv"
    venv.EnvBuilder(with_pip=True).create(environment_root)
    executable_directory = environment_root / ("Scripts" if os.name == "nt" else "bin")
    installed_python = executable_directory / ("python.exe" if os.name == "nt" else "python")
    forge = executable_directory / ("forge.exe" if os.name == "nt" else "forge")
    install_environment = _isolated_runtime_environment(tmp_path)
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
    installed_origin = _run(
        [
            str(installed_python),
            "-c",
            "from pathlib import Path; import forge_cli; "
            f"assert Path(forge_cli.__file__).resolve().is_relative_to(Path({str(environment_root)!r}).resolve());",
        ],
        cwd=tmp_path,
        environment=install_environment,
    )
    assert installed_origin.stdout == ""
    site_packages = Path(
        _run(
            [str(installed_python), "-c", "import site; print(site.getsitepackages()[0])"],
            cwd=tmp_path,
            environment=install_environment,
        ).stdout.strip()
    )
    (site_packages / "sitecustomize.py").write_text(_NETWORK_GUARD, encoding="utf-8")
    guard_marker = Path(install_environment["FORGE_WHEEL_GUARD_MARKER"])
    network_guard = _run(
        [
            str(installed_python),
            "-c",
            "import socket\n"
            "try:\n"
            "    socket.create_connection(('example.com', 443))\n"
            "except RuntimeError as error:\n"
            "    assert str(error) == 'network disabled by installed-wheel verification guard'\n"
            "else:\n"
            "    raise AssertionError('network guard did not deny outbound connection')",
        ],
        cwd=tmp_path,
        environment=install_environment,
    )
    assert network_guard.stdout == ""
    assert guard_marker.read_text(encoding="utf-8") == "loaded\n"
    probe = tmp_path / "adapter_cli_wheel_probe.py"
    shutil.copy2(Path(__file__).with_name("adapter_cli_wheel_probe.py"), probe)
    _run(
        [
            str(installed_python),
            str(probe),
            str(forge),
            str(repository),
            str(expected_protocol),
            str(expected_effective_flows),
            str(guard_marker),
        ],
        cwd=tmp_path,
        environment=install_environment,
    )
