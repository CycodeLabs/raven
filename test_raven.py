import utils
from config import Config


def get_nodes(node_type: str) -> int:
    nodes = utils.get_all(node_type)
    indexed_nodes = 0
    for node in nodes:
        if node.get('path').endswith('demo-workflow.yml'):
            indexed_nodes += 1
            node = dict(node)
    
    return indexed_nodes

def test_all_workflows() -> None:
    indexed_workflows = get_nodes('Workflow')

    assert indexed_workflows == 4

def test_all_jobs() -> None:
    indexed_jobs = get_nodes('Job')

    assert indexed_jobs == 4

def test_all_composite_actions() -> None:
    indexed_composite_actions = get_nodes('CompositeAction')

    assert indexed_composite_actions == 0

def test_all_steps() -> None:
    indexed_steps = get_nodes('Step')

    assert indexed_steps == 8


tests = [
    test_all_workflows,
    test_all_jobs,
    test_all_composite_actions,
    test_all_steps
]


def test():
    Config.load_default_index_config()
    for test in tests:
        test()


if __name__ == "__main__":
    test()