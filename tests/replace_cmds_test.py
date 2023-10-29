import json
import time
import pytest
from src.ca_pwt.commands import (
    replace_guids_with_attrs_cmd,
    replace_attrs_with_guids_cmd,
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
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_replace_guids_with_attrs_and_replace_attrs_with_guids(access_token: str):
    """Tests if the replace command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        input_file = "input_file.json"
        output_file = "output_file.json"

        # get the test data
        test_policies = get_valid_policies()
        with open("test_policies.json", "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_policies, indent=4))

        # we're going to inject an invalid key in the includeRoles node
        test_policies[0]["conditions"]["users"]["includeRoles"].append("00000000-0000-0000-0000-000000000000")

        with open(input_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_policies[0], indent=4))

        assert_valid_output_file(input_file)

        result = runner.invoke(
            replace_guids_with_attrs_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                input_file,
                "--output_file",
                output_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        assert_valid_output_file(output_file)

        with open(output_file) as f:
            data = json.load(f)

        assert data[0]["conditions"]["users"]["excludeGroupNames"]
        # check if the excludeGroups attribute is present but with only one member
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
            == test_policies[0]["conditions"]["users"]["includeRoles"][1]
        )

        # we're going to inject an invalid value in the includeRoleNames node
        data[0]["conditions"]["users"]["includeRoleNames"].append("test role")

        # write the test data to a file
        with open(input_file, "w") as f:
            f.write(json.dumps(data, indent=4))

        result = runner.invoke(
            replace_attrs_with_guids_cmd,
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

        # check if the file contains the expected node
        with open(output_file) as f:
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
