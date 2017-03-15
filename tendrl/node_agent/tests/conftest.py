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
    list_search = False
    with open(file_path, 'r') as f:
        for line in f:
            if not list_search:
                match = re.search("run:\s*(?P<run>[a-zA-Z0-9\._]+)", line)
                if match is not None:
                    functions.append(match.group("run"))
                    list_search = False
            else:
                match = re.search("- (?P<_run>[a-zA-Z0-9\._]+)", line)
                if match is not None:
                    functions.append(match.group("_run"))
                else:
                    list_search = False
            match2 = re.search("run:$", line)
            if match2 is not None:
                list_search = True
    return list(set(functions))


@pytest.fixture(params=get_defined_functions(definitions_path()))
def defined_function(request):
    """Generate function names for import."""

    return request.param
