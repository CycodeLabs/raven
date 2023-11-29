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
from src.indexer.utils import get_object_full_name_from_ref_pointers_set
from src.logger import log


def get_composite_action(path: str, commit_sha: str) -> Optional["CompositeAction"]:
    """
    Returns a composite action object from the graph.
    If not found, returns None.
    """
    ca = CompositeAction(None, path, commit_sha)
    obj = Config.graph.get_object(ca)
    return obj


def get_or_create_composite_action(path: str) -> "CompositeAction":
    """
    Used when need to create relations with another action.
    If action wasn't indexed yet, we create a stub node,
    that will be enriched eventually.
    """
    ca_full_name = get_object_full_name_from_ref_pointers_set(path)
    if ca_full_name:
        absolute_path, commit_sha = UsesString.split_path_and_ref(ca_full_name)
    else:
        log.warning(f"We did not download Composite Action - {path}")
        absolute_path, commit_sha = path, ""
    ###

    obj = get_composite_action(absolute_path, commit_sha)
    if not obj:
        # This is a legitimate behavior.
        # Once the action will be indexed, the node will be enriched.
        ca = CompositeAction(None, absolute_path, commit_sha)
        Config.graph.merge_object(ca)
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
    commit_sha = Property()
    action = RelatedTo("CompositeAction")

    def __init__(self, _id: str, path: str, commit_sha: str):
        self._id = _id
        self.path = path
        self.commit_sha = commit_sha

    @staticmethod
    def from_dict(obj_dict) -> "CompositeActionInput":
        i = CompositeActionInput(
            _id=obj_dict["_id"],
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
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
    shell = Property()
    url = Property()
    with_prop = Property("with")
    commit_sha = Property()

    action = RelatedTo("CompositeAction")
    using_param = RelatedTo(workflow.StepCodeDependency)

    def __init__(self, _id: str, path: str, commit_sha: str):
        self._id = _id
        self.path = path
        self.commit_sha = commit_sha

    @staticmethod
    def from_dict(obj_dict) -> "CompositeActionStep":
        s = CompositeActionStep(
            _id=obj_dict["_id"],
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )
        s.url = obj_dict["url"]
        if "id" in obj_dict:
            s.name = obj_dict["id"]
        if "run" in obj_dict:
            s.run = obj_dict["run"]

            # Adding ${{...}} dependencies as an entity.
            for code_dependency in get_dependencies_in_code(s.run):
                param = workflow.StepCodeDependency(
                    code_dependency, s.path, s.commit_sha
                )
                param.url = s.url
                s.using_param.add(param)

            if "shell" in obj_dict:
                s.shell = obj_dict["shell"]
        elif "uses" in obj_dict:
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of action steps, it may only reference actions (and not reusable workflows).
            uses_string_obj = UsesString.analyze(obj_dict["uses"], s.path)
            s.uses = uses_string_obj.absolute_path_with_ref
            if uses_string_obj.type == UsesStringType.ACTION:
                obj = get_or_create_composite_action(
                    uses_string_obj.absolute_path_with_ref
                )
                s.action.add(obj)

            if "with" in obj_dict:
                s.with_prop = convert_dict_to_list(obj_dict["with"])
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
    refs = Property()
    commit_sha = Property()

    composite_action_input = RelatedTo(CompositeActionInput)
    steps = RelatedTo(CompositeActionStep)

    def __init__(self, name: Optional[str], path: str, commit_sha: str):
        self.name = name
        self.path = path
        self.commit_sha = commit_sha
        self._id = md5(f"{path}_{commit_sha}".encode()).hexdigest()
        self.refs = []

    @staticmethod
    def from_dict(obj_dict) -> "CompositeAction":
        ca = CompositeAction(
            name=obj_dict.get("name"),
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )

        ca.url = obj_dict["url"]
        ca.is_public = obj_dict["is_public"]
        if "inputs" in obj_dict:
            for name, input in obj_dict["inputs"].items():
                input["_id"] = md5(
                    f"{ca._id}_{name}_{ca.commit_sha}".encode()
                ).hexdigest()
                input["name"] = name
                input["url"] = ca.url
                input["commit_sha"] = ca.commit_sha
                input["path"] = ca.path
                ca.composite_action_input.add(CompositeActionInput.from_dict(input))

        if "ref" in obj_dict:
            ca.refs.append(obj_dict["ref"])

        if "runs" in obj_dict:
            d_runs = obj_dict["runs"]

            if "using" in d_runs:
                ca.using = d_runs["using"]

            if "image" in d_runs:
                ca.image = d_runs["image"]

            if "steps" in d_runs:
                for i, step in enumerate(d_runs["steps"]):
                    step["_id"] = md5(
                        f"{ca._id}_{i}_{ca.commit_sha}".encode()
                    ).hexdigest()
                    step["path"] = ca.path
                    step["url"] = ca.url
                    step["commit_sha"] = ca.commit_sha
                    ca.steps.add(CompositeActionStep.from_dict(step))

        return ca
