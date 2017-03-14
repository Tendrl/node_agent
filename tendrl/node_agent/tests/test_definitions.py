import pkgutil


def test_defined_functions(defined_function):
    """Check if `defined_function` can be imported."""

    assert pkgutil.find_loader(defined_function)
