from typing import Optional, Dict, Any
from hashlib import md5

from py2neo.ogm import GraphObject, RelatedTo, RelatedFrom, Property
from src.config.config import Config
from src.common.utils import (
    get_dependencies_in_code,
    get_repo_name_from_path,
    convert_dict_to_list,
    find_workflow_by_name,
    raw_str_to_bool,
)
from src.workflow_components.parsing_utils import (
    parse_workflow_trigger,
    parse_job_machine,
)
from src.workflow_components.dependency import UsesString, UsesStringType
import src.logger.log as log


def get_or_create_workflow(path: str) -> "Workflow":
    """Used when need to create relations with another workflow.
    If workflow wasn't indexed yet, we create a stub node,
    that will be enriched eventually.
    """
    w = Workflow(None, path)
    obj = Config.graph.get_object(w)
    if not obj:
        # This is a legitimate behavior.
        # Once the workflow will be indexed, the node will be enriched.
        Config.graph.push_object(w)
        obj = w
    return obj


class StepCodeDependency(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    param = Property()
    url = Property()
    path = Property()

    def __init__(self, param: str, path: str):
        self.param = param
        self.path = path
        self._id = md5(f"{param}_{path}".encode()).hexdigest()


class Step(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    run = Property()
    uses = Property()
    ref = Property()
    with_prop = Property("with")
    url = Property()

    action = RelatedTo("src.workflow_components.composite_action.CompositeAction")
    reusable_workflow = RelatedTo("Workflow")
    using_param = RelatedTo("StepCodeDependency")

    def __init__(self, _id: str, name: Optional[str], path: str):
        self._id = _id
        self.name = name
        self.path = path

    @staticmethod
    def from_dict(obj_dict) -> "Step":
        s = Step(_id=obj_dict["_id"], name=obj_dict.get("name"), path=obj_dict["path"])
        s.url = obj_dict["url"]
        if "run" in obj_dict:
            s.run = obj_dict["run"]

            # Adding ${{...}} dependencies as an entity.
            for code_dependency in get_dependencies_in_code(s.run):
                param = StepCodeDependency(code_dependency, s.path)
                param.url = s.url
                s.using_param.add(param)
        elif "uses" in obj_dict:
            s.uses = obj_dict["uses"]
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of steps, it may only reference actions (and not reusable workflows).
            uses_string_obj = UsesString.analyze(uses_string=s.uses)
            if uses_string_obj.type == UsesStringType.ACTION:
                # Avoiding circular imports.
                import src.workflow_components.composite_action as composite_action

                obj = composite_action.get_or_create_composite_action(
                    uses_string_obj.get_full_path(s.path)
                )
                s.action.add(obj)

            if "with" in obj_dict:
                s.with_prop = convert_dict_to_list(obj_dict["with"])

            if len(s.uses.split("@")) > 1:
                s.ref = s.uses.split("@")[1]
        return s


class Job(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    machine = Property()
    uses = Property()
    ref = Property()
    url = Property()
    with_prop = Property("with")

    steps = RelatedTo(Step)
    reusable_workflow = RelatedTo("Workflow")

    def __init__(self, _id: str, name: str, path: str):
        self._id = _id
        self.name = name
        self.path = path

    @staticmethod
    def from_dict(obj_dict) -> "Job":
        j = Job(_id=obj_dict["_id"], name=obj_dict["name"], path=obj_dict["path"])
        if "uses" in obj_dict:
            j.uses = obj_dict["uses"]
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of jobs, it may only reference reusable workflows.
            uses_string_obj = UsesString.analyze(uses_string=j.uses)
            if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
                obj = get_or_create_workflow(uses_string_obj.get_full_path(j.path))
                j.reusable_workflow.add(obj)

            if "with" in obj_dict:
                j.with_prop = convert_dict_to_list(obj_dict["with"])

            if len(j.uses.split("@")) > 1:
                j.ref = j.uses.split("@")[1]

        j.url = obj_dict["url"]
        if "steps" in obj_dict:
            j.machine = parse_job_machine(obj_dict.get("runs-on"))

            for i, step in enumerate(obj_dict["steps"]):
                step["_id"] = md5(f"{j._id}_{i}".encode()).hexdigest()
                step["path"] = j.path
                step["url"] = j.url
                j.steps.add(Step.from_dict(step))

        return j


class Workflow(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    trigger = Property()
    permissions = Property()
    url = Property()
    is_public = Property()

    jobs = RelatedTo(Job)
    triggered_by = RelatedTo("Workflow")
    reusable_workflow_input = RelatedTo("ReusableWorkflowInput")

    def __init__(self, name: Optional[str], path: str):
        self.name = name
        self.path = path
        self._id = md5(path.encode()).hexdigest()

    @staticmethod
    def from_dict(obj_dict: Dict[str, Any]) -> "Workflow":
        w = Workflow(name=obj_dict.get("name"), path=obj_dict["path"])

        w.trigger = parse_workflow_trigger(obj_dict["on"])

        w.url = obj_dict["url"]
        w.is_public = obj_dict["is_public"]

        # Handling special case of workflow_run
        # When we meet it, we want to create a special relation from the triggering workflow,
        # to the triggered one.
        # There are cases where the triggering workflow wasn't loaded yet.
        # In that case we creating a stub node for it,
        # and once we'll meet it, we'll enrich it.
        if "workflow_run" in w.trigger:
            workflow_run = obj_dict["on"]["workflow_run"]
            triggering_workflows = workflow_run["workflows"]
            types = workflow_run["types"]
            for workflow_name in triggering_workflows:
                repo = get_repo_name_from_path(w.path)
                w_path = find_workflow_by_name(repo, workflow_name)
                if w_path is None:
                    log.debug(
                        f"[-] Couldn't find the triggering workflow '{workflow_name}' in repository '{repo}'"
                    )
                else:
                    w_triggering = get_or_create_workflow(w_path)
                    w.triggered_by.add(w_triggering, types=types)

        # Handling special case of workflow_call
        # When we meet it, we want to create a special relation to inputs of the reusable workflow.
        # We continue to treat the workflow as a regular workflow, and not as a reusable workflow.
        # But the difference is that we connected the different inputs to the workflow.
        if "workflow_call" in w.trigger:
            wokrflow_call = obj_dict["on"]["workflow_call"]
            inputs = wokrflow_call["inputs"]
            for input_name, input in inputs.items():
                input["_id"] = md5(f"{w._id}_{input_name}".encode()).hexdigest()
                input["name"] = input_name
                input["url"] = w.url
                input["path"] = w.path
                w.reusable_workflow_input.add(ReusableWorkflowInput.from_dict(input))

        if "permissions" in obj_dict:
            w.permissions = convert_dict_to_list(obj_dict["permissions"])

        for job_name, job in obj_dict["jobs"].items():
            if not isinstance(job, dict):
                log.error("[-] Invalid job structure")
                raise Exception("Invalid job structure.")
            job["_id"] = md5(f"{w._id}_{job_name}".encode()).hexdigest()
            job["path"] = w.path
            job["name"] = job_name
            job["url"] = w.url
            w.jobs.add(Job.from_dict(job))

        return w


class ReusableWorkflowInput(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    default = Property()
    description = Property()
    required = Property()
    path = Property()
    url = Property()

    def __init__(self, _id: str, path: str):
        self._id = _id
        self.path = path

    @staticmethod
    def from_dict(obj_dict) -> "ReusableWorkflowInput":
        i = ReusableWorkflowInput(_id=obj_dict["_id"], path=obj_dict["path"])
        i.name = obj_dict["name"]
        i.url = obj_dict["url"]

        if "default" in obj_dict:
            i.default = obj_dict.get("default")

        if "description" in obj_dict:
            i.description = obj_dict.get("description")

        i.required = raw_str_to_bool(obj_dict.get("required", "false"))

        return i
