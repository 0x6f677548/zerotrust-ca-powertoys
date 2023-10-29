import pytest
import time
from src.ca_pwt.commands import (
    import_groups_cmd,
)
from src.ca_pwt.groups import GroupsAPI
from .utils import SLEEP_BETWEEN_TESTS, get_valid_groups, get_invalid_groups, delete_test_groups
from .import_entity_cmd_test_utils import (
    _test_import_entity_duplicate,
    _test_import_entity_ignore,
    _test_import_entity_invalid_data,
    _test_import_entity_fail,
    _test_import_entity_overwrite,
)


@pytest.fixture(autouse=True)
def run_around_tests(access_token: str):
    delete_test_groups(access_token)
    yield
    delete_test_groups(access_token)
    # this is to avoid hitting the rate limit
    time.sleep(SLEEP_BETWEEN_TESTS)


def test_import_groups_duplicate(access_token: str):
    """Tests if the import-groups command works as expected when using the duplicate option"""
    _test_import_entity_duplicate(access_token, import_groups_cmd, GroupsAPI(access_token), get_valid_groups()[0])


def test_import_groups_ignore(access_token: str):
    """Tests if the import-groups command works as expected when using the ignore option"""
    _test_import_entity_ignore(access_token, import_groups_cmd, GroupsAPI(access_token), get_valid_groups()[0])


def test_import_groups_invalid_data(access_token: str):
    """Tests if the import-groups command works as expected when using invalid data"""
    _test_import_entity_invalid_data(access_token, import_groups_cmd, get_invalid_groups()[0])


def test_import_groups_fail(access_token: str):
    """Tests if the import-groups command works as expected when using the fail option"""
    _test_import_entity_fail(access_token, import_groups_cmd, GroupsAPI(access_token), get_valid_groups()[0])


def test_import_groups_overwrite(access_token: str):
    """Tests if the import-groups command works as expected when using the overwrite option"""
    _test_import_entity_overwrite(access_token, import_groups_cmd, GroupsAPI(access_token), get_valid_groups()[0])
