import json
import time
import pytest
from src.ca_pwt.commands import (
    export_groups_cmd,
)
from click.testing import CliRunner
from .utils import assert_valid_output_file, SLEEP_BETWEEN_TESTS, VALID_POLICIES


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_export_groups(access_token: str):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(VALID_POLICIES, indent=4))

        output_file = "export-groups.json"
        result = runner.invoke(
            export_groups_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
                "--output_file",
                output_file,
            ],
        )

        assert result.exit_code == 0
        assert_valid_output_file(output_file)
