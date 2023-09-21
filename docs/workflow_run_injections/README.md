# Workflow Run Injections
top do

## Queries


### Workflow Run + missing "path" param for download action

Source: https://www.legitsecurity.com/blog/artifact-poisoning-vulnerability-discovered-in-rust

Successful query with many results.
Victims: FluentUI, FastAPI

``` cypher
MATCH p=(w1:Workflow)-->(w2:Workflow)-[*]->(s:Step)-->(ca:CompositeAction) WHERE
(
    "pull_request" in w1.trigger OR
    "pull_request_target" in w1.trigger OR
    "issue_comment" in w1.trigger OR
    "issues" in w1.trigger
) AND (
    ca.path = "data/actions/dawidd6|action-download-artifact|action.yml" 
) AND (
    not ANY(param IN s.with WHERE 
        (
            param contains "path"
        )
    )
) AND
EXISTS {
        (w2)-[*]->(caTmp:CompositeAction)
        WHERE caTmp.path = "data/actions/actions|checkout|action.yml"
    }
RETURN DISTINCT w2.path;
```

### Workflow Run + Head Branch Injection

Few quality results.

``` cypher
MATCH p=(w1:Workflow)-->(w2:Workflow)-[*]->(scd:StepCodeDependency) WHERE
(
    "pull_request" in w1.trigger OR
    "pull_request_target" in w1.trigger
) AND scd.param = "github.event.workflow_run.head_branch"
RETURN DISTINCT p;
```

### Workflow run + PR ID Injection

``` cypher
MATCH p=(w1:Workflow)-->(w2:Workflow)-[*]->(s:Step) WHERE
(
    "pull_request" in w1.trigger OR
    "pull_request_target" in w1.trigger OR
    "issue_comment" in w1.trigger OR
    "issues" in w1.trigger
) AND (
    s.run CONTAINS "$(<pr-id.txt)"
)
RETURN DISTINCT w2.path;
```