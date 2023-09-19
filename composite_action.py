from typing import Optional
from hashlib import md5

from py2neo.ogm import GraphObject, RelatedTo, Property

import workflow
from utils import (
    get_dependencies_in_code,
    get_obj_from_uses_string,
    get_repo_full_name_from_fpath,
    convert_dict_to_list,
)


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
    reusable_workflow = RelatedTo(workflow.Workflow)
    using_param = RelatedTo(workflow.StepCodeDependency)

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
                param = workflow.StepCodeDependency(code_dependency)
                s.using_param.add(param)

            if "shell" in d:
                s.shell = d["shell"]
        elif "uses" in d:
            s.uses = d["uses"]
            obj = get_obj_from_uses_string(
                uses_string=s.uses, 
                relative_repo_full_name=(s.path),
                object_type=CompositeAction

            )
            if obj:
                if isinstance(obj, CompositeAction):
                    s.action.add(obj)
                elif isinstance(obj, workflow.Workflow):
                    s.reusable_workflow.add(obj)

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
