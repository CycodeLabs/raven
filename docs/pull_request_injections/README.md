# Pull Request Injections
fill this

## Queries
### Pull Request + Pull Request Title 
``` cypher
MATCH (w:Workflow)-[*]->(j:Job)-->(s:Step)-->(dep:StepCodeDependency)
WHERE
    w.permissions IS NULL AND
    "pull_request" IN w.trigger AND
    s.run IS NOT NULL AND
    dep.param = "github.event.pull_request.title"
RETURN DISTINCT w, j, s, dep;
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
RETURN DISTINCT w.path, w.url;
```
