from typing import Dict, Any, List, Union, Optional


def parse_workflow_trigger(
    trigger_obj: Union[str, List[str], Dict[str, Any]]
) -> List[str]:
    """Parse and normalize the trigger field of a workflow.
    Returns list of triggers.
    Examples for input and output:
        push -> ["push"]
        ["push"] -> ["push"]
        ["push", "pull_request"] -> ["push", "pull_request"]
        {
            "push": {
                "branches": [
                    "master"
                ]
            }
        } -> ["push"]
    """
    if isinstance(trigger_obj, str):
        trigger_list = [trigger_obj]
    elif isinstance(trigger_obj, list):
        trigger_list = []
        for elem in trigger_obj:
            if isinstance(elem, dict):
                trigger_list.extend(elem.keys())
            else:
                trigger_list.append(elem)
    elif isinstance(trigger_obj, dict):
        trigger_list = list(trigger_obj.keys())
    else:
        # Shouldn't happen.
        trigger_list = []

    return trigger_list


def parse_job_machine(
    runs_on_obj: Optional[Union[str, List[str], Dict[str, Any]]]
) -> Optional[List[str]]:
    """Parse runs-on field of a job.
    Examples for input and output:
        ubuntu-latest -> ["ubuntu-latest"]
        ["ubuntu-latest"] -> ["ubuntu-latest"]
        {
            "labels": [
                "ubuntu-latest"
            ]
        } -> ["ubuntu-latest"]
    """
    if isinstance(runs_on_obj, str):
        return [runs_on_obj]
    elif isinstance(runs_on_obj, list):
        return runs_on_obj
    elif isinstance(runs_on_obj, dict):
        return runs_on_obj["labels"]

    return None
