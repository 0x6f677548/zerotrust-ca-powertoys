import json
import time
import pytest
from src.ca_pwt.commands import (
    replace_keys_by_values_cmd,
    replace_values_by_keys_cmd,
)
from click.testing import CliRunner
from .utils import assert_valid_output_file, SLEEP_BETWEEN_TESTS, VALID_POLICIES


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_replace_keys_by_values_replace_values_by_keys(access_token: str):
    """Tests if the replace command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"

        # we're going to inject an invalid key in the includeRoles node
        VALID_POLICIES[0]["conditions"]["users"]["includeRoles"].append("00000000-0000-0000-0000-000000000000")

        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(VALID_POLICIES[0], indent=4))

        assert_valid_output_file(test_data_file)

        result = runner.invoke(
            replace_keys_by_values_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
                "--output_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        assert_valid_output_file(test_data_file)

        # check if the file contains the expected node
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert data[0]["conditions"]["users"]["excludeGroupNames"]
            # check if the previous node is present but with only one member
            # (an invalid one that wasn't able to be converted)
            assert len(data[0]["conditions"]["users"]["excludeGroups"]) == 1

            assert data[0]["conditions"]["users"]["includeGroupNames"]
            assert "includeGroups" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["excludeUserNames"]
            assert "excludeUsers" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["includeUserNames"]
            assert "includeUsers" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["excludeRoleNames"]
            assert "excludeRoles" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["includeRoleNames"]
            # this node has one item with an invalid key that wasn't able to be converted
            assert "includeRoles" in data[0]["conditions"]["users"]
            assert len(data[0]["conditions"]["users"]["includeRoles"]) == 1
            # check if the invalid key is still present
            assert (
                data[0]["conditions"]["users"]["includeRoles"][0]
                == VALID_POLICIES[0]["conditions"]["users"]["includeRoles"][1]
            )

            # we're going to inject an invalid value in the includeRoleNames node
            data[0]["conditions"]["users"]["includeRoleNames"].append("test role")

        # write the test data to a file
        with open(test_data_file, "w") as f:
            f.write(json.dumps(data, indent=4))

        result = runner.invoke(
            replace_values_by_keys_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
                "--output_file",
                test_data_file,
            ],
        )
        assert result.exit_code == 0
        assert_valid_output_file(test_data_file)

        # check if the file contains the expected node
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert data[0]["conditions"]["users"]["excludeGroups"]
            # check if the previous node was removed
            assert "excludeGroupNames" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["includeGroups"]
            assert "includeGroupNames" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["excludeUsers"]
            assert "excludeUserNames" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["includeUsers"]
            assert "includeUserNames" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["excludeRoles"]
            assert "excludeRoleNames" not in data[0]["conditions"]["users"]

            assert data[0]["conditions"]["users"]["includeRoles"]
            # this node has one item with an invalid value that wasn't able to be converted
            assert "includeRoleNames" in data[0]["conditions"]["users"]
            assert len(data[0]["conditions"]["users"]["includeRoleNames"]) == 1
