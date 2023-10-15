from src.entraid_tools.conditional_access.commands import (
    ca_export,
    ca_group_ids_to_names,
    ca_group_names_to_ids,
    ca_cleanup_for_import,
    ca_import,
)
from src.entraid_tools.conditional_access.graph_api import PoliciesAPI
from click.testing import CliRunner
import os
import test_data
import json


def assert_valid_policies_file(output_file):
    # check if file exists
    assert os.path.isfile(output_file)
    # check if file is not empty
    assert os.stat(output_file).st_size != 0

    # open file and check if it is valid json

    with open(output_file) as f:
        data = json.load(f)
        assert data

        # check if file contains the expected data
        # check if value is a list
        assert isinstance(data, list)
        # check if it contains any policies
        assert len(data) > 0


def test_ca_export_no_filter(access_token: str):
    """Test if the ca_export command works as expected (no filter)"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        output_file = "ca_export.json"
        result = runner.invoke(
            ca_export,
            [
                "--access_token",
                access_token,
                "--output_file",
                output_file,
            ],
        )

        assert result.exit_code == 0
        assert_valid_policies_file(output_file)


def test_ca_export_filter_by_name(access_token: str):
    """Test if the ca_export command works as expected (filter by name)"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        output_file = "ca_export.json"
        result = runner.invoke(
            ca_export,
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
        assert_valid_policies_file(output_file)


def test_ca_group_ids_to_names_ca_group_names_to_ids(access_token: str):
    """Tests if the ca_group_ids_to_names command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_data.policies, indent=4))

        assert_valid_policies_file(test_data_file)

        result = runner.invoke(
            ca_group_ids_to_names,
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
        assert_valid_policies_file(test_data_file)

        # check if the file contains the expected node
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert data[0]["conditions"]["users"]["excludeGroupNames"]
            # check if the previous node was removed
            assert "excludeGroups" not in data[0]["conditions"]["users"]

        result = runner.invoke(
            ca_group_names_to_ids,
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
        assert_valid_policies_file(test_data_file)

        # check if the file contains the expected node
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert data[0]["conditions"]["users"]["excludeGroups"]

            # check if the previous node was removed
            assert "excludeGroupNames" not in data[0]["conditions"]["users"]


def test_ca_cleanup_for_import():
    """Tests if the ca_cleanup_for_import command works as expected"""
    runner = CliRunner()

    # check that the test data has id, createdDateTime and modifiedDateTime
    assert test_data.policies[0]["id"]
    assert test_data.policies[0]["createdDateTime"]
    assert test_data.policies[0]["modifiedDateTime"]

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_data.policies, indent=4))

        assert_valid_policies_file(test_data_file)

        result = runner.invoke(
            ca_cleanup_for_import,
            [
                "--input_file",
                test_data_file,
                "--output_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        assert_valid_policies_file(test_data_file)

        # check if the file was cleaned up, by checking if the id, createdDateTime and modifiedDateTime are gone
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert "id" not in data[0]
            assert "createdDateTime" not in data[0]
            assert "modifiedDateTime" not in data[0]


def test_ca_import(access_token: str):
    """Tests if the ca_import command works as expected"""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_data.policies, indent=4))

        assert_valid_policies_file(test_data_file)

        result = runner.invoke(
            ca_import,
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
