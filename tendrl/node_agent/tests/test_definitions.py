import pkgutil
import yaml


def test_yaml_file_validity(definitions_node_agent_path_yaml):
    """Check if `definitions` file is in a valid YAML format."""

    # TODO(fbalak) validate against some schema
    # http://stackoverflow.com/questions/3262569/validating-a-yaml-document-in-python
    definitions = yaml.safe_load(definitions_node_agent_path_yaml)
    assert definitions is not None


def test_definitions_node_agent_run_attributes(definitions_run_attribute):
    """Check if `defined_function` can be imported."""

    assert pkgutil.find_loader(definitions_run_attribute)
