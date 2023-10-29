import json
from click.testing import CliRunner
from click.core import BaseCommand
from .utils import assert_valid_output_file
from src.ca_pwt.helpers.graph_api import EntityAPI


def _assert_entity_existence(
    entity_api: EntityAPI, entity_display_name: str, expected_count: int, message: str
) -> list[dict]:
    get_entities_response = entity_api.get_all(f"displayName eq '{entity_display_name}'")
    get_entities_response.assert_success()
    assert get_entities_response is not None
    entities = get_entities_response.json()["value"]
    assert entities is not None
    assert len(entities) == expected_count, message
    return entities


def _test_import_entity_ignore(access_token: str, cli: BaseCommand, entity_api: EntityAPI, test_entity: dict):
    """Tests if the import entity command works as expected"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        # use only the first policy
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_entity, indent=4))

        assert_valid_output_file(test_data_file)

        for _ in range(2):
            result = runner.invoke(
                cli,
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
        _assert_entity_existence(
            entity_api, test_entity["displayName"], 1, "Only one test entity should have been imported."
        )


def _test_import_entity_duplicate(access_token: str, cli: BaseCommand, entity_api: EntityAPI, test_entity: dict):
    """Tests if the import entity command works as expected when duplicating"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        # use only the first policy
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_entity, indent=4))

        assert_valid_output_file(test_data_file)

        for _ in range(2):
            result = runner.invoke(
                cli,
                [
                    "--access_token",
                    access_token,
                    "--input_file",
                    test_data_file,
                    "--duplicate_action",
                    "duplicate",
                ],
            )
            assert result is not None
            assert result.exit_code == 0

        # check if the policies were imported
        _assert_entity_existence(
            entity_api, test_entity["displayName"], 2, "Test entity was not imported or duplicated."
        )


def _test_import_entity_overwrite(access_token: str, cli: BaseCommand, entity_api: EntityAPI, test_entity: dict):
    """Tests if the import entity command works as expected when overwriting"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        # use only the first policy
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_entity, indent=4))

        assert_valid_output_file(test_data_file)

        for _ in range(2):
            result = runner.invoke(
                cli,
                ["--access_token", access_token, "--input_file", test_data_file, "--duplicate_action", "overwrite"],
            )
            assert result is not None
            assert result.exit_code == 0

        # check if the policies were imported
        _assert_entity_existence(
            entity_api, test_entity["displayName"], 1, "Test entity was not imported or overwritten."
        )


def _test_import_entity_fail(access_token: str, cli: BaseCommand, entity_api: EntityAPI, test_entity: dict):
    """Tests if the import-entity command works as expected when failing"""
    runner = CliRunner()

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        # use only the first policy
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_entity, indent=4))

        assert_valid_output_file(test_data_file)

        for i in range(2):
            result = runner.invoke(
                cli,
                ["--access_token", access_token, "--input_file", test_data_file, "--duplicate_action", "fail"],
            )
            assert result is not None
            if i == 0:
                assert result.exit_code == 0
            else:
                assert result.exit_code == 1

        # check if the policies were imported
        _assert_entity_existence(
            entity_api, test_entity["displayName"], 1, "A single test entity should have been imported."
        )


def _test_import_entity_invalid_data(access_token: str, cli: BaseCommand, test_entity: dict):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps({}, indent=4))

        result = runner.invoke(
            cli,
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
            f.write(json.dumps(test_entity, indent=4))

        result = runner.invoke(
            cli,
            [
                "--access_token",
                access_token,
                "--input_file",
                test_data_file,
            ],
        )

        assert result is not None
        assert result.exit_code == 1
