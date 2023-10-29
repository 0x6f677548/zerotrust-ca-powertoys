import json
import time
import pytest
from src.ca_pwt.commands import (
    export_groups_cmd,
)
from click.testing import CliRunner
from .utils import (
    assert_valid_output_file,
    SLEEP_BETWEEN_TESTS,
    get_valid_policies,
    import_test_groups,
    delete_test_groups,
)


@pytest.fixture(autouse=True)
def run_around_tests(access_token: str):
    import_test_groups(access_token)

    yield

    delete_test_groups(access_token)

    # this is to avoid hitting the rate limit if the tests are run too often
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_export_groups(access_token: str):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        input_file = "policies.json"
        with open(input_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(get_valid_policies(), indent=4))

        output_file = "export-groups.json"
        result = runner.invoke(
            export_groups_cmd,
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
