# GitHub Actions Indexer

We are indexing all popular (based on stars) repositories on GitHub, their workflows and actions, into a Neo4j database.
Once indexed, the data could be queries effectively to find vulnerabilities and missing best practices.
All vulnerable GitHub Actions found here are documented here: https://docs.google.com/spreadsheets/d/1OGGDFWHGBRwIa60d-XtOsLUq7PQavdj_IK2EWd4vmjY

## Usage

The tool contains two main functionalities, `download` and `index`.

### Download

``` bash
usage: main.py download [-h] --token TOKEN [--output OUTPUT]
                        [--max_stars MAX_STARS] [--min_stars MIN_STARS]

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN         GITHUB_TOKEN to download data from Github API
                        (Needed for effective rate-limiting)
  --output OUTPUT, -o OUTPUT
                        Output directory to download the workflows
  --max-stars MAX_STARS
                        Maximum number of stars for a repository
  --min-stars MIN_STARS
                        Minimum number of stars for a repository
```

### Index

``` bash
usage: main.py index [-h] [--input INPUT] [--neo4j-uri NEO4J_URI]
                     [--neo4j-user NEO4J_USER]
                     [--neo4j-pass NEO4J_PASS] [--threads THREADS]
                     [--clean]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        Input directory with the downloaded workflows
  --neo4j-uri NEO4J_URI
                        Neo4j URI endpoint
  --neo4j-user NEO4J_USER
                        Neo4j username
  --neo4j-pass NEO4J_PASS
                        Neo4j password
  --threads THREADS, -t THREADS
                        Number of threads
  --clean, -c           Whether to clean cache, and index from scratch
```

## Rate Limiting

For effective rate limiting, you should supply a Github token.
For authenticated users, the next rate limiting applies:
- Code search - 30 runs per minute
- Any other API - 5000 per hour

## Functionalities

### Downloader

- If workflow contains an action, the downloader will also download it (in the action folder).
- If the workflow references a reusable workflow, the downloader will also download it (in the workflow folder).

### Indexer

- If the indexer finds workflow uses an action, it will create a proper connection to it in the graph
- Same applies to reusable workflows
- Same applies to workflow triggered through `workflow_call`

## Issues

- It is possible to run GitHub Actions by referencing a folder with a `Dockerfile` (without `action.yml`). Currently, this behavior isn't supported (vscode: https://github.com/slsa-framework/slsa-github-generator/blob/main/.github/workflows/pre-submit.actions.yml).
- It is possible to run GitHub Actions by referencing a docker container through the `docker://...` URL. Currently, this behavior isn't supported.

## TODO

- Create better indexing for mapping inputs to outputs when calling actions to find misuse of that input
- Expand the research for findings of bad misuse of `GITHUB_ENV`
- Understand whether `actions/github-script` has an interesting threat landscape
- Bettering modeling of dictionary params, such as `with`.

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
RETURN w.path, j.name;
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
