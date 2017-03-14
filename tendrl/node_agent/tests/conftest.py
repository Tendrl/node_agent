import os
import pytest
import re


@pytest.fixture
def definitions_path():
    """Get absolute path to definitions file."""

    return os.path.abspath(os.path.dirname(os.path.realpath(__file__)) +
                           "/../../../etc/tendrl_definitions_node_agent.yaml")


def get_defined_functions(file_path):
    """Get list of runable functions from definitions."""

    functions = []
    with open(file_path, 'r') as f:
        for line in f:
            match = re.search("run:\s*(?P<run>[a-zA-Z0-9-._])*", line)
            if match is not None:
                functions.append(match.group())
    return functions


@pytest.fixture(params=get_defined_functions(definitions_path()))
def defined_function(request):
    """Generate function names for import."""

    return request.param
