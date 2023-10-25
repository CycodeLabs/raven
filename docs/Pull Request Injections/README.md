# Vulnerability Name

## Overview
Pull Requests (PRs) are a cornerstone of collaborative coding but can become a security loophole when integrated with automated workflows like GitHub Actions. Without proper input validation or sanitation, attackers can exploit this by injecting malicious code into PR titles, descriptions, or file changes. These injections can compromise the integrity of the entire codebase by executing unauthorized commands, code, or even exfiltrating sensitive information. This documentation aims to explore the vulnerabilities, real-world examples, remediation strategies, and detection techniques associated with pull request injections.


## Description
We will present two scenarios of pull request injections in vulnerable workflows:

### 1. pull_request + Pull Request Title:
In this scenario, workflows trigger on pull request events and execute jobs that depend on the pull request title (github.event.pull_request.title) without any permissions checks or input sanitization.
```yaml
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  use_pr_title:
    runs-on: ubuntu-latest
    steps:
    - name: Print PR Title
      run: echo "Pull Request Title is ${{ github.event.pull_request.title }}"
```

### 2. pull_request_target + Checkout
Using the `pull_request_target` event in a GitHub Actions workflow is risky because it runs in the context of the base repository, not the fork. This means it has access to secrets and write permissions to the repository. The real danger arises when such a workflow is combined with `checkout` action, which checks out code from an incoming, potentially untrusted pull request and then executes scripts or runs commands based on that code. Without proper permissions checks, this could allow a malicious actor to run untrusted code in a privileged environment, potentially leading to unauthorized access or data leaks.

```yaml
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  checkout_code:
    runs-on: ubuntu-latest
    steps:
    # Checks out code from the incoming pull request
    - name: Checkout code
      uses: actions/checkout@v2
      with:
        ref: ${{ github.event.pull_request.head.sha }}
    
    # Executes scripts or runs commands based on the checked out code
    - name: Build and deploy
      run: make deploy
```
## Remediation
* **Input Validation**: Sanitize and validate data from pull request titles or other user-generated fields before using them in your workflows.

* **Limited Permissions**: Minimize the permissions granted to GitHub Actions. Use read-only permissions where possible.

* **Workflow Segregation**: Consider using separate workflows for trusted and untrusted events to minimize risk.

* **Manual Approval**: Use manual approval of actions run.
  
## References
- [Cycode Discovers Vulnerabilities in CI/CD Pipelines of Popular Open-Source Projects](https://cycode.com/blog/github-actions-vulnerabilities/)

## Real-World Examples
### fauna/faunadb-js - 694 ⭐️
* **Description**: This workflow runs when a pull_request is created. Lines 32 and 33 use the pull request's body and title in an insecure manner, at `create-jira-tickets.yml`.
* **Fix Commit Link**: [ee6f53f9c985bde41976743530e3846dee058587](https://github.com/fauna/faunadb-js/commit/ee6f53f9c985bde41976743530e3846dee058587)
* **Remediation**: Removed the workflow.

## Queries
### 1. Pull Request + Pull Request Title 

This query looks for GitHub Actions workflows that are triggered by pull requests and specifically focuses on those that don't have defined permissions. It then identifies any jobs and steps within those workflows that use the pull request title (github.event.pull_request.title) in some way. The goal is to find potential security risks arising from the use of unsanitized pull request titles.

``` cypher
MATCH (w:Workflow)-[*]->(j:Job)-->(s:Step)-->(dep:StepCodeDependency)
WHERE
    w.permissions IS NULL AND
    "pull_request" IN w.trigger AND
    s.run IS NOT NULL AND
    dep.param = "github.event.pull_request.title"
RETURN DISTINCT w, j, s, dep;
```

### 2. Pull Request Target + Checkout

This query aims to identify workflows that are triggered by the `pull_request_target` event and don't have specified permissions. It then looks for jobs within those workflows that use the actions/checkout action to checkout code based on pull request data. The query focuses on parameters that start with "ref" and contain either head.sha or head.ref. Due to its broad nature, this query might produce many false positives, but it's designed to flag potentially risky configurations involving `pull_request_target` and code checkout.

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
RETURN DISTINCT w.path, w.url;
```
