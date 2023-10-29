from src.ca_pwt.commands import (
    cleanup_policies_cmd,
)
from .utils import get_valid_policies
from .cleanup_entity_cmd_test_utils import _test_cleanup_entity


def test_cleanup_policies():
    """Tests if the cleanup-policies command works as expected"""
    test_policies = get_valid_policies()
    _test_cleanup_entity(test_policies, cleanup_policies_cmd)
    # this will test the scenario where a dict is passed instead of a list
    _test_cleanup_entity(test_policies, cleanup_policies_cmd)
