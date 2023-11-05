### General Consts ###
RELATIONSHIP_TYPES = ["STEPS", "JOBS", "ACTION", "USING_PARAM"]

### Integration Consts ###

## Queries

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

## Integration 1 Repo

INTEGRAION_1_JSON_PATH = "tests/integration/structures_json/integration-1.json"
INTEGRAION_1_NODES_PATHS = [
    "RavenIntegrationTests/Integration-1/.github/workflows/integration-workflow.yml",
    "RavenIntegrationTests/CompositeAction-Mock",
]

### Node Count ###

DEMO_WORKFLOW_PATHS = [
    "RavenIntegrationTests/Demo-1/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-2/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-3/.github/workflows/demo-workflow.yml",
    "RavenIntegrationTests/Demo-4/.github/workflows/demo-workflow.yml",
]
