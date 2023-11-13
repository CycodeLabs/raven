## Queries ##

GET_RELATIONSHIPS_BY_PATH_QUERY = """
MATCH (s)-[r]->(e)
where s.path in {paths_list}
RETURN s, r, e
"""

GET_NODES_BY_PATH_QUERY = """
MATCH (s)
where s.path in {paths_list}
RETURN s
"""

START_NODE_INDEX = 0
DEST_NODE_INDEX = 2

## Tests Configs ##
TESTS_CONFIGS = [
    {
        "test_name": "test_integration_1",
        "json_path": "tests/integration/structures_json/integration-1.json",
        "description": "Tests Integration 1's graph structure. This is a repository with a single workflow. The workflow has Jobs, Steps, and StepCodeDependency. It uses a composite action which is also in the organization. The Composite Action has Steps and StepCodeDependency. These are all the node types that we currently support.",
        "queries": {
            "nodes_query": GET_NODES_BY_PATH_QUERY,
            "relationships_query": GET_RELATIONSHIPS_BY_PATH_QUERY,
            "to_format": {
                "paths_list": [
                    "RavenIntegrationTests/Integration-1/.github/workflows/integration-workflow.yml",
                    "RavenIntegrationTests/CompositeAction-Mock",
                ]
            },
        },
    },
    {
        "test_name": "test_demo_index_repos",
        "json_path": "tests/integration/structures_json/demo-index.json",
        "description": "Tests Demo-[1-4]'s graph structures combined. These are four different repositories that have similar workflows. They all have a workflow that uses the checkout action.",
        "queries": {
            "nodes_query": GET_NODES_BY_PATH_QUERY,
            "relationships_query": GET_RELATIONSHIPS_BY_PATH_QUERY,
            "to_format": {
                "paths_list": [
                    "RavenIntegrationTests/Demo-1/.github/workflows/demo-workflow.yml",
                    "RavenIntegrationTests/Demo-2/.github/workflows/demo-workflow.yml",
                    "RavenIntegrationTests/Demo-3/.github/workflows/demo-workflow.yml",
                    "RavenIntegrationTests/Demo-4/.github/workflows/demo-workflow.yml",
                    "actions/checkout",
                ]
            },
        },
    },
    {
        "test_name": "test_reusable_workflows",
        "json_path": "tests/integration/structures_json/reusable-workflows.json",
        "description": "Tests ReusableWorkflows-Mock's graph structure. This is a repository with two workflows. One of them uses the other as a reusable workflow.",
        "queries": {
            "nodes_query": GET_NODES_BY_PATH_QUERY,
            "relationships_query": GET_RELATIONSHIPS_BY_PATH_QUERY,
            "to_format": {
                "paths_list": [
                    "RavenIntegrationTests/ReusableWorkflows-Mock/.github/workflows/reuse_workflow.yml",
                    "RavenIntegrationTests/ReusableWorkflows-Mock/.github/workflows/test.yml",
                ]
            },
        },
    },
]
