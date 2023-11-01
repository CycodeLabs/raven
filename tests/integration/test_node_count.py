from tests.utils import get_nodes_as_dicts


DEMO_WORKFLOW_PATHS = [
    "RavenIntegrationTests/Demo-1/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-2/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-3/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-4/.github/workflows/demo-workflow.yml",
]


def test_all_workflows() -> None:
    nodes_details = get_nodes_as_dicts("Workflow", paths=DEMO_WORKFLOW_PATHS)

    for node in nodes_details:
        assert node.get("name") == "run"
        assert node.get("trigger") == ["workflow_dispatch"]
        assert node.get("is_public") == True

    assert len(nodes_details) == 4


def test_all_jobs() -> None:
    nodes_details = get_nodes_as_dicts("Job", paths=DEMO_WORKFLOW_PATHS)

    for node in nodes_details:
        assert node.get("name") == "demo_test"
        assert node.get("machine") == "ubuntu-latest"

    assert len(nodes_details) == 4


def test_all_composite_actions() -> None:
    nodes_details = get_nodes_as_dicts("CompositeAction", paths=DEMO_WORKFLOW_PATHS)

    for node in nodes_details:
        assert node.get("is_public") == True

    assert len(nodes_details) == 0


def test_all_steps() -> None:
    nodes_details = get_nodes_as_dicts("Step", paths=DEMO_WORKFLOW_PATHS)

    for node in nodes_details:
        assert node.get("name", "PrintEnv") == "PrintEnv"
        assert node.get("ref", "v4") == "v4"

    assert len(nodes_details) == 8
