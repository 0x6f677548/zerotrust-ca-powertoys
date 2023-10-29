import pytest
import time
from src.ca_pwt.commands import (
    import_policies_cmd,
)
from src.ca_pwt.policies import PoliciesAPI
from .utils import (
    SLEEP_BETWEEN_TESTS,
    get_valid_policies,
    get_invalid_policies,
    delete_test_groups,
    delete_test_policies,
    import_test_groups,
)
from .import_entity_cmd_test_utils import (
    _test_import_entity_duplicate,
    _test_import_entity_ignore,
    _test_import_entity_invalid_data,
    _test_import_entity_fail,
    _test_import_entity_overwrite,
)


@pytest.fixture(autouse=True)
def run_around_tests(access_token: str):
    delete_test_policies(access_token)
    import_test_groups(access_token)

    yield

    delete_test_policies(access_token)
    delete_test_groups(access_token)

    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_import_policies_ignore(access_token: str):
    """Tests if the import-policies command works as expected"""
    _test_import_entity_ignore(access_token, import_policies_cmd, PoliciesAPI(access_token), get_valid_policies()[0])


def test_import_policies_duplicating(access_token: str):
    """Tests if the import-policies command works as expected when duplicating"""
    _test_import_entity_duplicate(access_token, import_policies_cmd, PoliciesAPI(access_token), get_valid_policies()[0])


def test_import_policies_overwrite(access_token: str):
    """Tests if the import-policies command works as expected when overwriting"""
    _test_import_entity_overwrite(access_token, import_policies_cmd, PoliciesAPI(access_token), get_valid_policies()[0])


def test_import_policies_fail(access_token: str):
    """Tests if the import-policies command works as expected when failing"""
    _test_import_entity_fail(access_token, import_policies_cmd, PoliciesAPI(access_token), get_valid_policies()[0])


def test_import_policies_invalid_data(access_token: str):
    """Tests if the import-policies command works as expected when using invalid data"""
    _test_import_entity_invalid_data(access_token, import_policies_cmd, get_invalid_policies()[0])
