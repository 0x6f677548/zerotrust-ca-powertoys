from src.ca_pwt.commands import (
    cleanup_policies_cmd,
)
from .utils import VALID_POLICIES
from .cleanup_entity_cmd_test_utils import _test_cleanup_entity


def test_cleanup_policies():
    """Tests if the cleanup-policies command works as expected"""
    _test_cleanup_entity(VALID_POLICIES, cleanup_policies_cmd)
