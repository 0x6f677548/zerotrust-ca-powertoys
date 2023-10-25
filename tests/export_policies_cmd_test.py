import time
import pytest
from src.ca_pwt.commands import (
    export_policies_cmd,
)
from click.testing import CliRunner
from .utils import assert_valid_output_file, SLEEP_BETWEEN_TESTS


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_export_policies_no_filter(access_token: str):
    """Test if the export-policies command works as expected (no filter)"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        output_file = "export-policies.json"
        result = runner.invoke(
            export_policies_cmd,
            [
                "--access_token",
                access_token,
                "--output_file",
                output_file,
            ],
        )

        assert result.exit_code == 0
        assert_valid_output_file(output_file)


def test_export_policies_filter_by_name(access_token: str):
    """Test if the export-policies command works as expected (filter by name)"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        output_file = "export-policies.json"
        result = runner.invoke(
            export_policies_cmd,
            [
                "--access_token",
                access_token,
                "--output_file",
                output_file,
                "--odata_filter",
                "startswith(displayName, 'CA')",
            ],
        )

        assert result.exit_code == 0
        assert_valid_output_file(output_file)
