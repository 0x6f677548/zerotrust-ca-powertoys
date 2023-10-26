from src.ca_pwt.commands import (
    cleanup_groups_cmd,
)
from .utils import VALID_GROUPS
from .cleanup_entity_cmd_test_utils import _test_cleanup_entity


def test_cleanup_groups():
    """Tests if the cleanup-groups command works as expected"""
    _test_cleanup_entity(VALID_GROUPS, cleanup_groups_cmd)
    # this will test the scenario where a dict is passed instead of a list
    _test_cleanup_entity(VALID_GROUPS[0], cleanup_groups_cmd)
