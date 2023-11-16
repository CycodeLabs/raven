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
from src.indexer.utils import get_object_full_name_from_ref_pointers_set


def get_workflow(path: str, commit_sha: str) -> Optional["Workflow"]:
    """
    Returns a workflow object from the graph.
    If not found, returns None.
    """
    w = Workflow(None, path, commit_sha)
    obj = Config.graph.get_object(w)
    return obj


def get_or_create_workflow(path: str) -> "Workflow":
    """Used when need to create relations with another workflow.
    If workflow wasn't indexed yet, we create a stub node,
    that will be enriched eventually.
    """
    # TODO: This should be discussed. #
    w_full_name = get_object_full_name_from_ref_pointers_set(path)
    if w_full_name:
        absolute_path, commit_sha = UsesString.split_path_and_ref(w_full_name)
    else:
        log.warning(f"We did not download Workflow - {path}")
        absolute_path, commit_sha = path, ""
    ###
    w = Workflow(None, absolute_path, commit_sha)
    obj = Config.graph.get_object(w)
    if not obj:
        # This is a legitimate behavior.
        # Once the workflow will be indexed, the node will be enriched.
        Config.graph.merge_object(w)
        obj = w
    return obj


def get_or_create_workflow_run_workflow(path: str, commit_sha: str) -> "Workflow":
    """
    The reason we need this function is that we find the triggred workflow by searching all the workflows for name  by the workflow_run trigger

    """
    w = Workflow(None, path, commit_sha)
    obj = Config.graph.get_object(w)
    if not obj:
        # This is a legitimate behavior.
        # Once the workflow will be indexed, the node will be enriched.
        Config.graph.merge_object(w)
        obj = w
    return obj


class StepCodeDependency(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    param = Property()
    url = Property()
    path = Property()
    commit_sha = Property()

    def __init__(self, param: str, path: str, commit_sha: str):
        self.param = param
        self.path = path
        self.commit_sha = commit_sha
        self._id = md5(f"{param}_{path}_{commit_sha}".encode()).hexdigest()


class Step(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    run = Property()
    uses = Property()
    with_prop = Property("with")
    url = Property()
    commit_sha = Property()

    action = RelatedTo("src.workflow_components.composite_action.CompositeAction")
    reusable_workflow = RelatedTo("Workflow")
    using_param = RelatedTo("StepCodeDependency")

    def __init__(self, _id: str, name: Optional[str], path: str, commit_sha: str):
        self._id = _id
        self.name = name
        self.path = path
        self.commit_sha = commit_sha

    @staticmethod
    def from_dict(obj_dict) -> "Step":
        s = Step(
            _id=obj_dict["_id"],
            name=obj_dict.get("name"),
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )
        s.url = obj_dict["url"]
        if "run" in obj_dict:
            s.run = obj_dict["run"]

            # Adding ${{...}} dependencies as an entity.
            for code_dependency in get_dependencies_in_code(s.run):
                param = StepCodeDependency(code_dependency, s.path, s.commit_sha)
                param.url = s.url
                s.using_param.add(param)
        elif "uses" in obj_dict:
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of steps, it may only reference actions (and not reusable workflows).
            uses_string_obj = UsesString.analyze(obj_dict["uses"], s.path)
            s.uses = uses_string_obj.absolute_path_with_ref
            if uses_string_obj.type == UsesStringType.ACTION:
                # Avoiding circular imports.
                import src.workflow_components.composite_action as composite_action

                obj = composite_action.get_or_create_composite_action(
                    uses_string_obj.absolute_path_with_ref
                )
                s.action.add(obj)

            if "with" in obj_dict:
                s.with_prop = convert_dict_to_list(obj_dict["with"])

        return s


class Job(GraphObject):
    __primarykey__ = "_id"

    _id = Property()
    name = Property()
    path = Property()
    machine = Property()
    uses = Property()
    url = Property()
    with_prop = Property("with")
    commit_sha = Property()

    steps = RelatedTo(Step)
    reusable_workflow = RelatedTo("Workflow")

    def __init__(self, _id: str, name: str, path: str, commit_sha: str):
        self._id = _id
        self.name = name
        self.path = path
        self.commit_sha = commit_sha

    @staticmethod
    def from_dict(obj_dict) -> "Job":
        j = Job(
            _id=obj_dict["_id"],
            name=obj_dict["name"],
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )
        if "uses" in obj_dict:
            # Uses string is quite complex, and may reference to several types of nodes.
            # In the case of jobs, it may only reference reusable workflows.
            uses_string_obj = UsesString.analyze(obj_dict["uses"], j.path)
            j.uses = uses_string_obj.absolute_path_with_ref
            if uses_string_obj.type == UsesStringType.REUSABLE_WORKFLOW:
                obj = get_or_create_workflow(uses_string_obj.absolute_path_with_ref)
                j.reusable_workflow.add(obj)

            if "with" in obj_dict:
                j.with_prop = convert_dict_to_list(obj_dict["with"])

        j.url = obj_dict["url"]
        if "steps" in obj_dict:
            j.machine = parse_job_machine(obj_dict.get("runs-on"))

            for i, step in enumerate(obj_dict["steps"]):
                step["_id"] = md5(f"{j._id}_{i}_{j.commit_sha}".encode()).hexdigest()
                step["path"] = j.path
                step["url"] = j.url
                step["commit_sha"] = j.commit_sha
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
    commit_sha = Property()
    refs = Property()

    jobs = RelatedTo(Job)
    triggered_by = RelatedFrom("Workflow")
    reusable_workflow_input = RelatedTo("ReusableWorkflowInput")

    def __init__(self, name: Optional[str], path: str, commit_sha: str):
        self.name = name
        self.path = path
        self.commit_sha = commit_sha
        self._id = md5(f"{path}_{commit_sha}".encode()).hexdigest()
        self.refs = []

    @staticmethod
    def from_dict(obj_dict: Dict[str, Any]) -> "Workflow":
        w = Workflow(
            name=obj_dict.get("name"),
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )

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
                    w_triggering = get_or_create_workflow_run_workflow(
                        *UsesString.split_path_and_ref(w_path)
                    )
                    w.triggered_by.add(w_triggering, types=types)

        # Handling special case of workflow_call
        # When we meet it, we want to create a special relation to inputs of the reusable workflow.
        # We continue to treat the workflow as a regular workflow, and not as a reusable workflow.
        # But the difference is that we connected the different inputs to the workflow.
        if "workflow_call" in w.trigger:
            wokrflow_call = obj_dict["on"]["workflow_call"]
            inputs = wokrflow_call["inputs"]
            for input_name, input in inputs.items():
                input["_id"] = md5(
                    f"{w._id}_{input_name}_{w.commit_sha}".encode()
                ).hexdigest()
                input["name"] = input_name
                input["url"] = w.url
                input["path"] = w.path
                input["commit_sha"] = w.commit_sha
                w.reusable_workflow_input.add(ReusableWorkflowInput.from_dict(input))

        if "permissions" in obj_dict:
            w.permissions = convert_dict_to_list(obj_dict["permissions"])

        if "ref" in obj_dict:
            w.refs.append(obj_dict["ref"])

        for job_name, job in obj_dict["jobs"].items():
            if not isinstance(job, dict):
                log.error("[-] Invalid job structure")
                raise Exception("Invalid job structure.")
            job["_id"] = md5(f"{w._id}_{job_name}".encode()).hexdigest()
            job["path"] = w.path
            job["name"] = job_name
            job["commit_sha"] = w.commit_sha
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
    commit_sha = Property()

    def __init__(self, _id: str, path: str, commit_sha: str):
        self._id = _id
        self.path = path
        self.commit_sha = commit_sha

    @staticmethod
    def from_dict(obj_dict) -> "ReusableWorkflowInput":
        i = ReusableWorkflowInput(
            _id=obj_dict["_id"],
            path=obj_dict["path"],
            commit_sha=obj_dict["commit_sha"],
        )
        i.name = obj_dict["name"]
        i.url = obj_dict["url"]

        if "default" in obj_dict:
            i.default = obj_dict.get("default")

        if "description" in obj_dict:
            i.description = obj_dict.get("description")

        i.required = raw_str_to_bool(obj_dict.get("required", "false"))

        return i
