import src.workflow_components.workflow as workflow
from tests.utils import load_test_config, assert_reusable_workflow_inputs

load_test_config()


def test_job_from_dict_steps():
    job_d = {
        "name": "issue-commented",
        "runs-on": "ubuntu-latest",
        "steps": [
            {
                "name": "Generate GitHub App token",
                "uses": "electron/github-app-auth-action@cc6751b3b5e4edc5b9a4ad0a021ac455653b6dc8",
                "id": "generate-token",
                "with": {"creds": "${{ secrets.ISSUE_TRIAGE_GH_APP_CREDS }}"},
            },
        ],
        "_id": "6347a06af34cc01c884c110fd9db8964",
        "path": "electron/electron/.github/workflows/issue-commented.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
    }

    job = workflow.Job.from_dict(job_d)

    assert job._id == job_d["_id"]
    assert job.name == job_d["name"]
    assert job.path == job_d["path"]
    assert job.machine == [job_d["runs-on"]]
    assert job.uses is None
    assert job.ref is None
    assert job.with_prop is None
    assert job.url == job_d["url"]
    assert len(job.steps) == 1
    assert len(job.reusable_workflow) == 0


def test_workflow_from_dict():
    workflow_d = {
        "name": "Release notes",
        "on": {"push": {"branches": ["main"]}, "workflow_dispatch": None},
        "permissions": {"contents": "read"},
        "jobs": {
            "update_release_draft": {
                "permissions": {"contents": "write", "pull-requests": "write"},
                "runs-on": "ubuntu-latest",
                "if": "github.repository == 'twbs/bootstrap'",
                "steps": [
                    {
                        "uses": "release-drafter/release-drafter@v5",
                        "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                    }
                ],
            }
        },
        "path": "twbs/bootstrap/.github/workflows/release-notes.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
    }

    wf = workflow.Workflow.from_dict(workflow_d)

    assert wf.name == workflow_d["name"]
    assert wf.path == workflow_d["path"]
    assert wf.trigger == ["push", "workflow_dispatch"]
    assert wf.permissions == ["contents:read"]
    assert wf.url == workflow_d["url"]
    assert len(wf.jobs) == 1


def test_job_from_dict_uses():
    job_d = {
        "name": "test-firefox-safari",
        "uses": "./.github/workflows/build_reusable.yml",
        "with": {
            "skipForDocsOnly": "yes",
        },
        "secrets": "inherit",
        "_id": "f796b4c01ecb6021e6a30ec7466ab11a",
        "path": "vercel/next.js/.github/workflows/build_and_test.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
    }

    job = workflow.Job.from_dict(job_d)

    assert job._id == job_d["_id"]
    assert job.name == job_d["name"]
    assert job.path == job_d["path"]
    assert job.machine is None
    assert job.uses == job_d["uses"]
    assert job.ref is None
    assert job.url == job_d["url"]
    assert job.with_prop == ["skipForDocsOnly:yes"]
    assert len(job.steps) == 0


def test_step_from_dict_uses():
    step_d = {
        "name": "Generate GitHub App token",
        "uses": "electron/github-app-auth-action@cc6751b3b5e4edc5b9a4ad0a021ac455653b6dc8",
        "with": {"creds": "${{ secrets.ISSUE_TRIAGE_GH_APP_CREDS }}"},
        "_id": "9a42f7bb6c8e5be00c1d36d54ac7bdb6",
        "path": "electron/electron/.github/workflows/issue-commented.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
    }

    step = workflow.Step.from_dict(step_d)

    assert step._id == step_d["_id"]
    assert step.name == step_d["name"]
    assert step.path == step_d["path"]
    assert step.run is None
    assert step.uses == step_d["uses"]
    assert step.url == step_d["url"]
    assert step.ref == "cc6751b3b5e4edc5b9a4ad0a021ac455653b6dc8"
    assert step.with_prop == ["creds:${{ secrets.ISSUE_TRIAGE_GH_APP_CREDS }}"]


def test_step_from_dict_run():
    step_d = {
        "name": "Autolabel based on affected areas",
        "run": "echo ${{ github.event.issue.body }}",
        "_id": "1386cfbaf5513e27c090 133287e01fe",
        "path": "vercel/next.js/.github/workflows/issue_validator.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
    }

    step = workflow.Step.from_dict(step_d)

    assert step._id == step_d["_id"]
    assert step.name == step_d["name"]
    assert step.path == step_d["path"]
    assert step.uses is None
    assert step.run == step_d["run"]
    assert step.ref is None
    assert step.url == step_d["url"]
    assert step.with_prop is None
    assert len(step.using_param) == 1


def test_reusable_workflow_from_dict():
    workflow_d = {
        "name": "Release notes",
        "on": {
            "workflow_call": {
                "inputs": {
                    "input_1": {
                        "required": True,
                        "default": "default_value_1",
                        "description": "description_1",
                    },
                    "input_2": {
                        "required": False,
                        "default": "default_value_2",
                        "description": "description_2",
                    },
                }
            }
        },
        "permissions": {"contents": "read"},
        "jobs": {
            "update_release_draft": {
                "permissions": {"contents": "write", "pull-requests": "write"},
                "runs-on": "ubuntu-latest",
                "if": "github.repository == 'twbs/bootstrap'",
                "steps": [
                    {
                        "uses": "release-drafter/release-drafter@v5",
                        "env": {"GITHUB_TOKEN": "${{ secrets.GITHUB_TOKEN }}"},
                    }
                ],
            }
        },
        "path": "twbs/bootstrap/.github/workflows/release-notes.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
    }

    wf = workflow.Workflow.from_dict(workflow_d)

    assert wf.name == workflow_d["name"]
    assert wf.path == workflow_d["path"]
    assert wf.trigger == ["workflow_call"]
    assert wf.permissions == ["contents:read"]
    assert wf.url == workflow_d["url"]
    assert len(wf.jobs) == 1

    assert_reusable_workflow_inputs(wf, workflow_d)
