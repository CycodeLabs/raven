from py2neo import Graph
from py2neo.ogm import GraphObject
from py2neo.data import Node
from typing import Tuple, Optional
import logger


class GraphDb(object):
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def push_object(self, obj: GraphObject):
        self.graph.merge(obj)

    def get_object(self, obj: GraphObject) -> Optional[GraphObject]:
        """Tries to find an object in the graph.
        Returns None if wasn't found.
        """
        matched_obj = obj.__class__.match(self.graph, obj._id)
        if not matched_obj.exists():
            return None
        else:
            return matched_obj.first()

    def get_or_create(self, obj: GraphObject) -> Tuple[GraphObject, bool]:
        """Tries to find a similar object using given object _id.
        If found one, returns it, together with True value.
        If not found, inserting the object given, and returns it with False value.
        """
        matched_obj = obj.__class__.match(self.graph, obj._id)
        if not matched_obj.exists():
            logger.warning(
                f"WARNING: We didn't found object {obj._id} of type {obj.__class__.__name__}, so we created it."
            )
            self.graph.push(obj)
            return obj, False
        else:
            return matched_obj.first(), True

    def get_all(self, node_type: str) -> list[Node]:
        """
        Returns all nodeTypes nodes in the graph.
        NodeType:
            1) Job
            2) CompositeAction
            3) Workflow
            4) Step
        """
        return list(self.graph.nodes.match(node_type))

    def clean_graph(self):
        self.graph.delete_all()

    def run_predefined_queries(self):
        detection_results = []
        for detection in detections:
            query = detection.get("query", "")
            result = self.graph.run(query)
            results = [record for record in result]

            detection_results.append(
                {
                    "name": detection.get("name", ""),
                    "description": detection.get("description", ""),
                    "results": [dict(result) for result in results],
                }
            )

        return detection_results


detections = [
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
