# CodeSee Injections

## Overview
CodeSee is a startup company providing methods to visualize your codebase and effective tooling for reviewing and collaboration. Similar to other developer-centric products (e.g., CodeCov), during CodeSee integration, it creates a new Github Actions workflow that embeds its capabilities for every pull request, allowing developers efficiently review the added code. Cycode discovered a branch name injection vulnerability in `codesee-map-action` that may allow Remote Code Execution (RCE) on the pipeline.

## Description
Calling `Codesee-io/codesee-map-action` action up to the vulnerable versions with branch name containing malicious code injection payload such as `a";ls;"` allowed to inject code to CodeSee NPM package. Malicious threat actors can create a malicious script file that would be fetched together with a forked pull request that will be executed inside the pipeline.

## Remediation
This issue was fixed in version `0.376.0`. CodeSee’s internal review discovered this injection vulnerability entered their system as a result of a logical bug in the code used to escape the user-supplied branch name. In addition to repairing that logic directly, they replaced all command executions in their code analysis to run without a shell, ensuring no subtle escaping logic was required. As the CLI is written in node, this involved replacing calls to child_process.exec with child_process.execFile.

To further mitigate any other future vulnerabilities, CodeSee introduced the following permissions in the workflow to minimize that:
``` yaml
permissions: read-all
```
Even if such vulnerabilities have been found, the GITHUB_TOKEN won’t have sufficient permissions to perform any malicious activity.

## References
- [Cycode Collaborates with CodeSee to Secure the Pipelines of Thousands of Open-Source Projects](https://cycode.com/blog/cycode-secures-thousands-of-open-source-projects/)

## Real-World Examples
### freeCodeCamp/freeCodeCamp - 374K ⭐️

* **Description**: This workflow used `Codesee-io/codesee-map-action` latest version with `mapUpload` parameter.
* **Commit Link**: [0871341c9cbf96ab455bc3e0bce636e2ef2a2be2](https://github.com/freeCodeCamp/freeCodeCamp/commit/0871341c9cbf96ab455bc3e0bce636e2ef2a2be2)
* **Remediation**: Removed usage of CodeSee map action.

### slimtoolkit/slim - 17.3K ⭐️

* **Description**: This workflow used `Codesee-io/codesee-map-action` latest version with `mapUpload` parameter.
* **Commit Link**: [bb846649cb3dfaad83c3b2ccbee552786c7dc635](https://github.com/slimtoolkit/slim/commit/bb846649cb3dfaad83c3b2ccbee552786c7dc635)
* **Remediation**: Removed usage of CodeSee map action.

### statelyai/xstate - 24.8K ⭐️

* **Description**: This workflow used `Codesee-io/codesee-map-action` latest version with `mapUpload` parameter.
* **Commit Link**: N/A
* **Remediation**: Updated Through CodeSee package fix.

## Detections

### CodeSee Usage
Initially, verify if the workflow hasn't altered the default workflow permissions, then confirm if the workflow uses the `Codesee-io/codesee-map-action` action. Then, verify manually that the workflow is using the vulnerable versions.

``` cypher
MATCH (w:Workflow)
WHERE
    w.permissions is null AND
    EXISTS {
        (w)-[*]->(ca:CompositeAction)
        WHERE (
            ca.path = "Codesee-io/codesee-map-action"
        )
    }
RETURN DISTINCT w.path, w.url;
```