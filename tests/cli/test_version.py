from typer.testing import CliRunner

from forge_cli.app import app


runner = CliRunner()


def test_version_reports_cli_and_supported_protocol_versions() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "Forge CLI 0.1.0.dev0" in result.stdout
    assert "Forge Protocol 1" in result.stdout
    assert "1-draft" not in result.stdout
