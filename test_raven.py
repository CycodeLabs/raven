import utils
from config import Config


def get_nodes(node_type: str) -> (int, list):
    nodes = utils.get_all(node_type)
    indexed_nodes = 0
    nodes_details = []
    for node in nodes:
        if node.get("path").endswith("demo-workflow.yml"):
            indexed_nodes += 1
            node = dict(node)
            nodes_details.append(node)

    return indexed_nodes, nodes_details


def test_all_workflows() -> None:
    indexed_workflows, nodes_details = get_nodes("Workflow")

    for node in nodes_details:
        assert node.get("name") == "run"
        assert node.get("trigger") == ["workflow_dispatch"]

    assert indexed_workflows == 4


def test_all_jobs() -> None:
    indexed_jobs, nodes_details = get_nodes("Job")

    for node in nodes_details:
        assert node.get("name") == "demo_test"
        assert node.get("machine") == "ubuntu-latest"

    assert indexed_jobs == 4


def test_all_composite_actions() -> None:
    indexed_composite_actions, _ = get_nodes("CompositeAction")

    assert indexed_composite_actions == 0


def test_all_steps() -> None:
    indexed_steps, nodes_details = get_nodes("Step")

    for node in nodes_details:
        assert node.get("name", "PrintEnv") == "PrintEnv"
        assert node.get("ref", "v4") == "v4"

    assert indexed_steps == 8


def test():
    Config.load_default_index_config()
    for test in tests:
        test()


if __name__ == "__main__":
    tests = [
        test_all_workflows,
        test_all_jobs,
        test_all_composite_actions,
        test_all_steps,
    ]
    test()
