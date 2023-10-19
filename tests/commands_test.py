from src.ca_pwt.commands import (
    export_policies_cmd,
    replace_keys_by_values_cmd,
    replace_values_by_keys_cmd,
    cleanup_policies_cmd,
    import_policies_cmd,
)
from src.ca_pwt.policies import PoliciesAPI
from click.testing import CliRunner
import os
from .test_data import valid_policies, invalid_policies
import json


def _assert_valid_policies_file(output_file):
    # check if file exists
    assert os.path.isfile(output_file)
    # check if file is not empty
    assert os.stat(output_file).st_size != 0

    # open file and check if it is valid json

    with open(output_file) as f:
        data = json.load(f)
        assert data

        # check if file contains the expected data
        # check if value is a single policy or is a list with a policy

        assert "displayName" in data or (
            isinstance(data, list) and len(data) > 0 and "displayName" in data[0]
        )


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
        _assert_valid_policies_file(output_file)


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
                "--filter",
                "startswith(displayName, 'CA')",
            ],
        )

        assert result.exit_code == 0
        _assert_valid_policies_file(output_file)


def test_replace_keys_by_values_replace_values_by_keys(access_token: str):
    """Tests if the replace command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(valid_policies, indent=4))

        _assert_valid_policies_file(test_data_file)

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
        _assert_valid_policies_file(test_data_file)

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
            assert "includeRoles" not in data[0]["conditions"]["users"]

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
        _assert_valid_policies_file(test_data_file)

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
            assert "includeRoleNames" not in data[0]["conditions"]["users"]


def _test_cleanup_policies(test_data_policies):
    runner = CliRunner()

    # we might receive a list of policies or a single policy
    if isinstance(test_data_policies, list):
        first_policy = test_data_policies[0]
    else:
        first_policy = test_data_policies

    # check that the test data has id, createdDateTime and modifiedDateTime
    assert "id" in first_policy
    assert "createdDateTime" in first_policy
    assert "modifiedDateTime" in first_policy

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_data_policies, indent=4))

        _assert_valid_policies_file(test_data_file)

        result = runner.invoke(
            cleanup_policies_cmd,
            [
                "--input_file",
                test_data_file,
                "--output_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        _assert_valid_policies_file(test_data_file)

        # check if the file was cleaned up, by checking if the id, createdDateTime and modifiedDateTime are gone
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert "id" not in data[0]
            assert "createdDateTime" not in data[0]
            assert "modifiedDateTime" not in data[0]


def test_cleanup_policies():
    """Tests if the cleanup-policies command works as expected"""

    _test_cleanup_policies(valid_policies)
    _test_cleanup_policies(valid_policies[0])


def test_import_policies(access_token: str):
    """Tests if the import-policies command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(valid_policies, indent=4))

        _assert_valid_policies_file(test_data_file)

        result = runner.invoke(
            import_policies_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0

        # check if the policies were imported
        policiesAPI = PoliciesAPI(access_token)
        get_policies_response = policiesAPI.get_all("displayName eq 'TEST-POLICY'")
        assert get_policies_response is not None
        policies = get_policies_response.json()["value"]
        assert policies is not None
        assert len(policies) == 1

        # clean up
        policiesAPI.delete(policies[0]["id"])


def test_import_policies_invalid_data(access_token: str):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps({}, indent=4))

        result = runner.invoke(
            import_policies_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 1

        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(invalid_policies, indent=4))

        result = runner.invoke(
            import_policies_cmd,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
            ],
        )

        assert result is not None
        assert result.exit_code == 1
