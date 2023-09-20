# Injections


## Queries

### Issue + Run Command Injection

Successful query with many results

``` cypher
MATCH (w:Workflow)-[*]->(d:StepCodeDependency)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger OR
        "pull_request_target" in w.trigger
    ) AND
    (
        d.param IN ["github.event.issue.title", "github.event.issue.body", "github.event.pull_request.title", "github.event.pull_request.body", "github.event.comment.body", "github.event.review.body", "github.event.review_comment.body", "github.event.pages.*.page_name", "github.event.commits.*.message", "github.event.head_commit.message", "github.event.head_commit.author.email", "github.event.head_commit.author.name", "github.event.commits.*.author.email", "github.event.commits.*.author.name", "github.event.pull_request.head.ref", "github.event.pull_request.head.label", "github.event.pull_request.head.repo.default_branch", "github.head_ref"]
    )
RETURN DISTINCT w.path;
```

### Pull Request Target + Checkout

Successful query with many results. Has many false positives.

``` cypher
MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    w.permissions is null AND
    "pull_request_target" in w.trigger AND
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ANY(param IN s.with WHERE
                (
                    param STARTS WITH "ref" and 
                    (
                        param contains "head.sha" OR
                        param contains "head.ref"
                    )
                )
            )
        )
    }
RETURN DISTINCT w.path;
```

### Issue Comment + Checkout

Successful query with many results.

``` cypher
MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger
    ) AND
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ca.path = "data/actions/actions|checkout|action.yml" AND
            ANY(param IN s.with WHERE 
                (
                    param STARTS WITH "ref" and 
                    (
                        param contains "head.sha" OR
                        param contains "head.ref"
                    )
                )
            )
        )
    }
RETURN w.path
```

### CodeSee Usage

Successful query with many results.
Article: https://cycode.com/cycode-secures-thousands-of-open-source-projects/

``` cypher
MATCH (w:Workflow)
WHERE
    w.permissions is null AND
    EXISTS {
        (w)-[*]->(ca:CompositeAction)
        WHERE (
            ca.path = "data/actions/Codesee-io|codesee-map-action|action.yml"
        )
    }
RETURN DISTINCT w.path;
```

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


### Workflow issue injection

``` cypher
MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger
    ) AND (
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ca.path = "peter-evans/find-comment" and
            EXISTS {
                (j)-->(s:Step)
                WHERE (
                    s.run contains "outputs.comment-body" or
                    s.with contains "outputs.comment-body"
                )
            }
        )
    } OR EXISTS {
        (j)-->(s:Step) WHERE (
            s.run contains "event.issue.title" or
            s.run contains "event.issue.body"
        )
    }
)

RETURN w.path
```