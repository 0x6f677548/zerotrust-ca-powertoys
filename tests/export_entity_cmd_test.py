import json
import time
import pytest
from src.ca_pwt.commands import (
    export_policies_cmd,
    export_policy_groups_cmd,
)
from click.testing import CliRunner
from .utils import (
    assert_valid_output_file,
    SLEEP_BETWEEN_TESTS,
    get_valid_policies,
    import_test_groups,
    import_test_policies,
    delete_test_policies,
    delete_test_groups,
)


@pytest.fixture(autouse=True)
def run_around_tests(access_token: str):
    import_test_groups(access_token)
    import_test_policies(access_token)

    yield
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)

    delete_test_policies(access_token)
    delete_test_groups(access_token)


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
        # grab the first 2 characters of the first policy's name and use it as a filter
        test_policy_prefix = get_valid_policies()[0]["displayName"][0:2]
        result = runner.invoke(
            export_policies_cmd,
            [
                "--access_token",
                access_token,
                "--output_file",
                output_file,
                "--odata_filter",
                f"startswith(displayName, '{test_policy_prefix}')",
            ],
        )

        assert result.exit_code == 0
        assert_valid_output_file(output_file)


def test_export_policy_groups_cmd(access_token: str):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        input_file = "policies.json"
        with open(input_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(get_valid_policies(), indent=4))

        output_file = "export-policy-groups.json"
        result = runner.invoke(
            export_policy_groups_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                input_file,
                "--output_file",
                output_file,
            ],
        )

        assert result.exit_code == 0
        assert_valid_output_file(output_file)
