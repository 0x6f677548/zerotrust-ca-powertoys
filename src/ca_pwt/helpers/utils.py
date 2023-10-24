def assert_condition(condition: any, message: str):
    """Asserts a condition and raises an AssertionError if it is False"""
    if not condition:
        raise AssertionError(message)
