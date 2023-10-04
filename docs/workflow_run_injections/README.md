# Workflow Run Injections
TODO

## Overview
TODO

## Description
TODO

## Remediation
TODO

## References
TODO

## Real-World Examples
### Repository Name

* **Description**: Briefly describe the vulnerability that was present in this repository's GitHub Actions workflow.
* **Commit Link**: Provide links to the specific commits in the repository where the vulnerability existed.
* **Remediation**: Explain how the vulnerability was fixed in this repository. Include links to relevant code changes or pull requests.


## Detections

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
    ca.path = "dawidd6/action-download-artifact" 
) AND (
    not ANY(param IN s.with WHERE 
        (
            param contains "path"
        )
    )
) AND
EXISTS {
        (w2)-[*]->(caTmp:CompositeAction)
        WHERE caTmp.path = "actions/checkout"
    }
RETURN DISTINCT w2.path, w2.url;
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
RETURN DISTINCT w2.path, w2.url;
```