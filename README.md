# GitHub Actions Indexer

We are indexing all popular (based on stars) repositories on GitHub, their workflows and actions, into a Neo4j database.
Once indexed, the data could be queries effectively to find vulnerabilities and missing best practices.
All vulnerable GitHub Actions found here are documented here: https://docs.google.com/spreadsheets/d/1OGGDFWHGBRwIa60d-XtOsLUq7PQavdj_IK2EWd4vmjY


## Setup

Clone Raven repository.
``` bash
git clone https://github.com/CycodeLabs/Raven.git
cd Raven
```

Build and run `neo4j` && `redis` containers.
``` bash
make setup
```

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

- [Injections](/docs/injections/README.md)