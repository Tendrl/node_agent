import pkgutil
import yaml


def test_valid_definitions(definitions_path):
    """Check if `definitions` file is in a valid YAML format."""

    # TODO(fbalak) validate against some schema
    # http://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python
    definitions = yaml.safe_load(definitions_path)
    assert definitions is not None


def test_defined_functions(defined_function):
    """Check if `defined_function` can be imported."""

    assert pkgutil.find_loader(defined_function)
