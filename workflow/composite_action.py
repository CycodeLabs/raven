from typing import Optional
from hashlib import md5

from py2neo.ogm import GraphObject, RelatedTo, Property

import workflow.handler as handler
from config.config import Config
from common.utils import (
    get_dependencies_in_code,
    convert_dict_to_list,
)
from workflow.dependency import UsesString, UsesStringType


def get_or_create_composite_action(path: str) -> "CompositeAction":
    """Used when need to create relations with another action.
    If action wasn't indexed yet, we create a stub node,
    that will be enriched eventually.
    """
    ca = CompositeAction(None, path)
    obj = Config.graph.get_object(ca)
    if not obj:
        # This is a legitimate behavior.
        # Once the action will be indexed, the node will be enriched.
        Config.graph.push_object(ca)
        obj = ca
    return obj


class CompositeActionStep(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    run = Property()
    uses = Property()
    ref = Property()
    shell = Property()
    with_prop = Property("with")

    action = RelatedTo("CompositeAction")
    reusable_workflow = RelatedTo(handler.Workflow)
    using_param = RelatedTo(handler.StepCodeDependency)

    def __init__(self, _id: str, path: str):
        self._id = _id
        self.path = path

    @staticmethod
    def from_dict(d) -> "CompositeActionStep":
        s = CompositeActionStep(_id=d["_id"], path=d["path"])
        if "id" in d:
            s.name = d["id"]
        if "run" in d:
            s.run = d["run"]

            # Adding ${{...}} dependencies as an entity.
            for code_dependency in get_dependencies_in_code(s.run):
                param = handler.StepCodeDependency(code_dependency)
                s.using_param.add(param)

            if "shell" in d:
                s.shell = d["shell"]
        elif "uses" in d:
            s.uses = d["uses"]
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of action steps, it may only reference actions (and not reusable workflows).
            uses_string_obj = UsesString.analyze(uses_string=s.uses)
            if uses_string_obj.type == UsesStringType.ACTION:
                obj = get_or_create_composite_action(
                    uses_string_obj.get_full_path(s.path)
                )
                s.action.add(obj)

            if "with" in d:
                s.with_prop = convert_dict_to_list(d["with"])

            if len(s.uses.split("@")) > 1:
                s.ref = s.uses.split("@")[1]

        return s


class CompositeAction(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    inputs = Property()
    using = Property()
    image = Property()

    steps = RelatedTo(CompositeActionStep)

    def __init__(self, name: Optional[str], path: str):
        self.name = name
        self.path = path
        self._id = md5(path.encode()).hexdigest()

    @staticmethod
    def from_dict(d) -> "CompositeAction":
        ca = CompositeAction(name=d.get("name"), path=d["path"])

        if "inputs" in d:
            ca.inputs = list(d["inputs"].keys())

        if "runs" in d:
            d_runs = d["runs"]

            if "using" in d_runs:
                ca.using = d_runs["using"]

            if "image" in d_runs:
                ca.image = d_runs["image"]

            if "steps" in d_runs:
                for i, step in enumerate(d_runs["steps"]):
                    step["_id"] = md5(f"{ca._id}_{i}".encode()).hexdigest()
                    step["path"] = ca.path
                    ca.steps.add(CompositeActionStep.from_dict(step))

        return ca
