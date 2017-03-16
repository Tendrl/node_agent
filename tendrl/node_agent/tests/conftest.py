import os
import pytest
import re


@pytest.fixture
def definitions_node_agent_path_yaml():
    """Get absolute path to definitions file."""

    return os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","..","..","etc/tendrl_definitions_node_agent.yaml"))

def get_run_attributes_from_yaml(file_path):
    """Get list of runable functions from definitions."""

    functions = set()
    list_search = False
    with open(file_path, 'r') as f:
        for line in f:
            if not list_search:
                match = re.search("run:\s*(?P<run>[a-zA-Z0-9\._]+)", line)
                if match is not None:
                    functions.add(match.group("run"))
                    list_search = False
            else:
                match = re.search("- (?P<_run>[a-zA-Z0-9\._]+)", line)
                if match is not None:
                    functions.add(match.group("_run"))
                else:
                    list_search = False
            match2 = re.search("run:$", line)
            if match2 is not None:
                list_search = True
    return list(functions)


@pytest.fixture(params=get_run_attributes_from_yaml(definitions_node_agent_path_yaml()))
def definitions_run_attribute(request):
    """Generate function names for import."""

    return request.param
