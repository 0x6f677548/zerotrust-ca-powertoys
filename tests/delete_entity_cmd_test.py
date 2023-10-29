import json
import pytest
import time
from click.testing import CliRunner
from click.core import BaseCommand

from src.ca_pwt.helpers.graph_api import EntityAPI
from src.ca_pwt.helpers.graph_api import APIResponse
from src.ca_pwt.policies import PoliciesAPI
from src.ca_pwt.groups import GroupsAPI

from src.ca_pwt.commands import (
    delete_policies_cmd,
    delete_groups_cmd,
)
from .utils import (
    SLEEP_BETWEEN_TESTS,
    import_test_policies,
    delete_test_policies,
    import_test_groups,
    delete_test_groups,
)


@pytest.fixture(autouse=True)
def run_around_tests():
    yield
    # this is to avoid hitting the rate limit if the tests are run too often
    time.sleep(SLEEP_BETWEEN_TESTS)


def _test_delete_entity(access_token: str, cli: BaseCommand, entity_api: EntityAPI):
    runner = CliRunner()
    with runner.isolated_filesystem():
        # obtain the test entities from the graph api
        response: APIResponse = entity_api.get_all(odata_filter="startswith(displayName, 'UNIT-TEST-')")
        response.assert_success(error_message=f"Failed to get test entities from {entity_api.__class__.__name__} API")
        from src.ca_pwt.helpers.utils import cleanup_odata_dict, ensure_list

        test_entities: list[dict] = ensure_list(cleanup_odata_dict(response.json()))

        # write the test data to a file
        input_file = "delete-entities.json"
        with open(input_file, "w") as f:
            f.write(json.dumps(test_entities, indent=4))
        result = runner.invoke(
            cli,
            [
                "--access_token",
                access_token,
                "--input_file",
                input_file,
            ],
        )

        assert result.exit_code == 0


def test_delete_policies(access_token: str):
    import_test_groups(access_token)
    import_test_policies(access_token)
    _test_delete_entity(access_token, delete_policies_cmd, PoliciesAPI(access_token=access_token))
    delete_test_policies(access_token)
    delete_test_groups(access_token)


def test_delete_groups(access_token: str):
    import_test_groups(access_token)
    _test_delete_entity(access_token, delete_groups_cmd, GroupsAPI(access_token=access_token))
    delete_test_groups(access_token)
