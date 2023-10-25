import pytest
import time
from src.ca_pwt.commands import (
    import_policies_cmd,
)
from src.ca_pwt.policies import PoliciesAPI
from .utils import SLEEP_BETWEEN_TESTS, VALID_POLICIES, INVALID_POLICIES
from .import_entity_cmd_test_utils import (
    _test_import_entity_duplicate,
    _test_import_entity_ignore,
    _test_import_entity_invalid_data,
    _test_import_entity_fail,
    _test_import_entity_replace,
    remove_entities,
)


@pytest.fixture(autouse=True)
def run_around_tests(access_token: str):
    # remove test policies
    policies_api = PoliciesAPI(access_token=access_token)
    for policy in VALID_POLICIES:
        remove_entities(policies_api, policy["displayName"])
    yield

    # remove test policies
    for policy in VALID_POLICIES:
        remove_entities(policies_api, policy["displayName"])

    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_import_policies_ignore(access_token: str):
    """Tests if the import-policies command works as expected"""
    _test_import_entity_ignore(access_token, import_policies_cmd, PoliciesAPI(access_token), VALID_POLICIES[0])


def test_import_policies_duplicating(access_token: str):
    """Tests if the import-policies command works as expected when duplicating"""
    _test_import_entity_duplicate(access_token, import_policies_cmd, PoliciesAPI(access_token), VALID_POLICIES[0])


def test_import_policies_replace(access_token: str):
    """Tests if the import-policies command works as expected when replacing"""
    _test_import_entity_replace(access_token, import_policies_cmd, PoliciesAPI(access_token), VALID_POLICIES[0])


def test_import_policies_fail(access_token: str):
    """Tests if the import-policies command works as expected when failing"""
    _test_import_entity_fail(access_token, import_policies_cmd, PoliciesAPI(access_token), VALID_POLICIES[0])


def test_import_policies_invalid_data(access_token: str):
    """Tests if the import-policies command works as expected when using invalid data"""
    _test_import_entity_invalid_data(access_token, import_policies_cmd, INVALID_POLICIES[0])
