# CodeSee Injections
fill this


## Queries


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
            ca.path = "Codesee-io/codesee-map-action"
        )
    }
RETURN DISTINCT w.path;
```