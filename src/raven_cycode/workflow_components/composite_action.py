from typing import Optional
from hashlib import md5

from py2neo.ogm import GraphObject, RelatedTo, Property

import src.workflow_components.workflow as workflow
from src.config.config import Config
from src.common.utils import (
    get_dependencies_in_code,
    convert_dict_to_list,
    raw_str_to_bool,
)
from src.workflow_components.dependency import UsesString, UsesStringType


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


class CompositeActionInput(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    default = Property()
    description = Property()
    required = Property()
    url = Property()
    path = Property()

    def __init__(self, _id: str, path: str):
        self._id = _id
        self.path = path

    @staticmethod
    def from_dict(obj_dict) -> "CompositeActionInput":
        i = CompositeActionInput(
            _id=obj_dict["_id"],
            path=obj_dict["path"],
        )

        i.name = obj_dict["name"]
        i.url = obj_dict["url"]

        if "default" in obj_dict:
            i.default = obj_dict["default"]

        if "description" in obj_dict:
            i.description = obj_dict["description"]

        i.required = raw_str_to_bool(obj_dict.get("required", "false"))

        return i


class CompositeActionStep(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    run = Property()
    uses = Property()
    ref = Property()
    shell = Property()
    url = Property()
    with_prop = Property("with")

    action = RelatedTo("CompositeAction")
    using_param = RelatedTo(workflow.StepCodeDependency)

    def __init__(self, _id: str, path: str):
        self._id = _id
        self.path = path

    @staticmethod
    def from_dict(obj_dict) -> "CompositeActionStep":
        s = CompositeActionStep(_id=obj_dict["_id"], path=obj_dict["path"])
        s.url = obj_dict["url"]
        if "id" in obj_dict:
            s.name = obj_dict["id"]
        if "run" in obj_dict:
            s.run = obj_dict["run"]

            # Adding ${{...}} dependencies as an entity.
            for code_dependency in get_dependencies_in_code(s.run):
                param = workflow.StepCodeDependency(code_dependency, s.path)
                param.url = s.url
                s.using_param.add(param)

            if "shell" in obj_dict:
                s.shell = obj_dict["shell"]
        elif "uses" in obj_dict:
            s.uses = obj_dict["uses"]
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of action steps, it may only reference actions (and not reusable workflows).
            uses_string_obj = UsesString.analyze(uses_string=s.uses)
            if uses_string_obj.type == UsesStringType.ACTION:
                obj = get_or_create_composite_action(
                    uses_string_obj.get_full_path(s.path)
                )
                s.action.add(obj)

            if "with" in obj_dict:
                s.with_prop = convert_dict_to_list(obj_dict["with"])

            if len(s.uses.split("@")) > 1:
                s.ref = s.uses.split("@")[1]

        return s


class CompositeAction(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    using = Property()
    image = Property()
    url = Property()
    is_public = Property()

    composite_action_input = RelatedTo(CompositeActionInput)
    steps = RelatedTo(CompositeActionStep)

    def __init__(self, name: Optional[str], path: str):
        self.name = name
        self.path = path
        self._id = md5(path.encode()).hexdigest()

    @staticmethod
    def from_dict(obj_dict) -> "CompositeAction":
        ca = CompositeAction(name=obj_dict.get("name"), path=obj_dict["path"])

        ca.url = obj_dict["url"]
        ca.is_public = obj_dict["is_public"]
        if "inputs" in obj_dict:
            for name, input in obj_dict["inputs"].items():
                input["_id"] = md5(f"{ca._id}_{name}".encode()).hexdigest()
                input["name"] = name
                input["url"] = ca.url
                input["path"] = ca.path
                ca.composite_action_input.add(CompositeActionInput.from_dict(input))

        if "runs" in obj_dict:
            d_runs = obj_dict["runs"]

            if "using" in d_runs:
                ca.using = d_runs["using"]

            if "image" in d_runs:
                ca.image = d_runs["image"]

            if "steps" in d_runs:
                for i, step in enumerate(d_runs["steps"]):
                    step["_id"] = md5(f"{ca._id}_{i}".encode()).hexdigest()
                    step["path"] = ca.path
                    step["url"] = ca.url
                    ca.steps.add(CompositeActionStep.from_dict(step))

        return ca
