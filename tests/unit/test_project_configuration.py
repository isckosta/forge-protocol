from pathlib import Path

import pytest

from forge_cli import configuration


VALID_CONFIG = """\
schema: forge/project@1
project:
  name: demo
forge:
  protocol: 1
flows:
  default: standard
  allow_fast: true
  auto_escalation: true
testing:
  approach: tdd_first
review:
  strict: true
documentation:
  impact_evaluation: required
harnesses: []
"""


def write_config(tmp_path: Path, content: str) -> Path:
    forge_dir = tmp_path / ".forge"
    forge_dir.mkdir()
    path = forge_dir / "forge.yml"
    path.write_text(content)
    return path


def test_loads_valid_project_configuration(tmp_path: Path) -> None:
    path = write_config(tmp_path, VALID_CONFIG)

    result = configuration.load_project_configuration(path)

    assert result["schema"] == "forge/project@1"
    assert result["project"]["name"] == "demo"
    assert result["forge"]["protocol"] == 1


def test_rejects_configuration_that_violates_project_schema(tmp_path: Path) -> None:
    invalid = VALID_CONFIG.replace("approach: tdd_first", "approach: test_after")
    path = write_config(tmp_path, invalid)

    with pytest.raises(configuration.InvalidProjectConfigurationError) as error:
        configuration.load_project_configuration(path)

    assert error.value.code == "E_FORGE_INVALID_PROJECT_CONFIGURATION"


def test_rejects_unsupported_protocol_version(tmp_path: Path) -> None:
    unsupported = VALID_CONFIG.replace("protocol: 1", "protocol: 999")
    path = write_config(tmp_path, unsupported)

    with pytest.raises(configuration.UnsupportedProtocolVersionError) as error:
        configuration.load_project_configuration(path)

    assert error.value.code == "E_FORGE_UNSUPPORTED_PROTOCOL"
    assert error.value.protocol == 999


def test_validation_is_deterministic_for_identical_repository_state(tmp_path: Path) -> None:
    path = write_config(tmp_path, VALID_CONFIG)

    first = configuration.load_project_configuration(path)
    second = configuration.load_project_configuration(path)

    assert first == second
