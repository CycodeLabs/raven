PREDEFINED_DETECTIONS = [
    {
        "name": "Issue Title/Body Injection",
        "description": "Issue Injection caused by github.event.issue.title/body.",
        "query": """MATCH (w:Workflow)-[*]->(d:StepCodeDependency)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger
    ) AND
    (
        d.param IN ["github.event.issue.title", "github.event.issue.body"]
    )
RETURN DISTINCT w.path;
""",
    },
    {
        "name": "Issue Comment Injection",
        "description": "Issue Injection",
        "query": """MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger
    ) AND
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ca.path = "actions/checkout" AND
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
RETURN DISTINCT w.path""",
    },
    {
        "name": "Pull Request Target Injection",
        "description": "",
        "query": """MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    w.permissions is null AND
    "pull_request_target" in w.trigger AND
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ca.path = "actions/checkout" AND
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
RETURN DISTINCT w.path;""",
    },
    {
        "name": "",
        "description": "",
        "query": """MATCH (w:Workflow)-[*]->(j:Job)
WHERE
    (
        "issue_comment" in w.trigger OR
        "issues" in w.trigger
    ) AND
    EXISTS {
        (j)-->(s:Step)-->(ca:CompositeAction)
        WHERE (
            ca.path = "actions/checkout" AND
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
RETURN w.path""",
    },
    {
        "name": "",
        "description": "",
        "query": """MATCH (w:Workflow)
WHERE
    w.permissions is null AND
    EXISTS {
        (w)-[*]->(ca:CompositeAction)
        WHERE (
            ca.path = "Codesee-io/codesee-map-action"
        )
    }
RETURN DISTINCT w.path;""",
    },
    {
        "name": "",
        "description": "",
        "query": """MATCH p=(w1:Workflow)-->(w:Workflow)-[*]->(s:Step)-->(ca:CompositeAction) WHERE
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
        (w)-[*]->(caTmp:CompositeAction)
        WHERE caTmp.path = "actions/checkout"
    }
RETURN DISTINCT w.path;""",
    },
    {
        "name": "",
        "description": "",
        "query": """MATCH p=(w1:Workflow)-->(w:Workflow)-[*]->(s:Step) WHERE
(
    "pull_request" in w1.trigger OR
    "pull_request_target" in w1.trigger OR
    "issue_comment" in w1.trigger OR
    "issues" in w1.trigger
) AND (
    s.run CONTAINS "$(<pr-id.txt)"
)
RETURN DISTINCT w.path;""",
    },
]
