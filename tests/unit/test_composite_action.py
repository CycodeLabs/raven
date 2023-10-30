import src.workflow_components.composite_action as composite_action
from tests.utils import load_test_config

load_test_config()


def test_composite_action_from_dist_node():
    ca_d = {
        "name": "Create Issue From File",
        "description": "An action to create an issue using content from a file",
        "inputs": {
            "token": {
                "description": "The GitHub authentication token",
                "default": "${{ github.token }}",
            },
            "repository": {
                "description": "The target GitHub repository",
                "default": "${{ github.repository }}",
            },
            "issue-number": {
                "description": "The issue number of an existing issue to update"
            },
            "title": {"description": "The title of the issue", "required": "true"},
            "content-filepath": {"description": "The file path to the issue content"},
            "labels": {"description": "A comma or newline-separated list of labels"},
            "assignees": {
                "description": "A comma or newline-separated list of assignees (GitHub usernames)"
            },
        },
        "outputs": {"issue-number": {"description": "The number of the created issue"}},
        "runs": {"using": "node16", "main": "dist/index.js"},
        "branding": {"icon": "alert-circle", "color": "orange"},
        "path": "data/actions/peter-evans|create-issue-from-file|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
        "tag": "v3",
    }

    ca = composite_action.CompositeAction.from_dict(ca_d)

    assert ca.name == ca_d["name"]
    assert ca.path == ca_d["path"]
    assert ca.inputs == list(ca_d["inputs"].keys())
    assert ca.using == "node16"
    assert ca.url == ca_d["url"]
    assert ca.is_public == ca_d["is_public"]
    assert ca.tag == ca_d["tag"]
    assert ca.image is None
    assert len(ca.steps) == 0


def test_composite_action_from_dict_dockerfile():
    ca_d = {
        "name": "Automatic Rebase",
        "description": "Automatically rebases PR on '/rebase' comment",
        "maintainer": "Cirrus Labs",
        "runs": {"using": "docker", "image": "Dockerfile"},
        "inputs": {
            "autosquash": {
                "description": "Should the rebase autosquash fixup and squash commits",
                "required": "false",
                "default": "false",
            }
        },
        "branding": {"icon": "git-pull-request", "color": "purple"},
        "path": "data/actions/cirrus-actions|rebase|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
    }

    ca = composite_action.CompositeAction.from_dict(ca_d)

    assert ca.name == ca_d["name"]
    assert ca.path == ca_d["path"]
    assert ca.inputs == list(ca_d["inputs"].keys())
    assert ca.using == "docker"
    assert ca.image == "Dockerfile"
    assert ca.url == ca_d["url"]
    assert ca.is_public == ca_d["is_public"]
    assert len(ca.steps) == 0


def test_composite_action_from_dict_image():
    ca_d = {
        "name": "Image Actions",
        "author": "Calibre",
        "description": "Compresses Images for the Web",
        "inputs": {
            "githubToken": {"description": "GitHub Token", "required": "true"},
        },
        "outputs": {
            "markdown": {
                "description": "Output param used to store the Markdown summary for subsequent actions to use"
            }
        },
        "runs": {
            "using": "docker",
            "image": "docker://ghcr.io/calibreapp/image-actions/image-actions:main",
        },
        "branding": {"icon": "image", "color": "green"},
        "path": "data/actions/calibreapp|image-actions|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
    }

    ca = composite_action.CompositeAction.from_dict(ca_d)

    assert ca.name == ca_d["name"]
    assert ca.path == ca_d["path"]
    assert ca.inputs == list(ca_d["inputs"].keys())
    assert ca.using == "docker"
    assert ca.url == ca_d["url"]
    assert ca.is_public == ca_d["is_public"]
    assert ca.image == "docker://ghcr.io/calibreapp/image-actions/image-actions:main"
    assert len(ca.steps) == 0


def test_composite_action_from_dict_steps():
    ca_d = {
        "name": "Install development tools",
        "description": "GitHub Action for installing development tools",
        "inputs": {
            "tool": {
                "description": "Tools to install (comma-separated list)",
                "required": "true",
            },
            "checksum": {
                "description": "Whether to enable checksums",
                "required": "false",
                "default": "true",
            },
        },
        "runs": {
            "using": "composite",
            "steps": [
                {
                    "run": 'bash --noprofile --norc "${GITHUB_ACTION_PATH:?}/main.sh"',
                    "shell": "bash",
                    "env": {
                        "INPUT_TOOL": "${{ inputs.tool }}",
                        "INPUT_CHECKSUM": "${{ inputs.checksum }}",
                    },
                }
            ],
        },
        "path": "data/actions/taiki-e|install-action|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "is_public": True,
        "tag": "v1",
    }

    ca = composite_action.CompositeAction.from_dict(ca_d)

    assert ca.name == ca_d["name"]
    assert ca.path == ca_d["path"]
    assert ca.inputs == list(ca_d["inputs"].keys())
    assert ca.using == "composite"
    assert ca.url == ca_d["url"]
    assert ca.is_public == ca_d["is_public"]
    assert ca.tag == ca_d["tag"]
    assert ca.image is None
    assert len(ca.steps) == 1


def test_composite_action_step_from_dict_run():
    step_d = {
        "run": ': install rustup if needed\nif ! command -v rustup &>/dev/null; then\n  curl --proto \'=https\' --tlsv1.2 --retry 10 --retry-connrefused --location --silent --show-error --fail "https://sh.rustup.rs" | sh -s -- --default-toolchain none -y\n  echo "${CARGO_HOME:-$HOME/.cargo}/bin" >> $GITHUB_PATH\nfi\n',
        "if": "runner.os != 'Windows'",
        "shell": "bash",
        "_id": "4eba12855ade10f6e8dda0456946ffa1",
        "path": "data/actions/dtolnay|rust-toolchain|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "tag": "v1",
    }

    step = composite_action.CompositeActionStep.from_dict(step_d)

    assert step._id == step_d["_id"]
    assert step.name is None
    assert step.path == step_d["path"]
    assert step.run == step_d["run"]
    assert step.uses is None
    assert step.ref is None
    assert step.shell == step_d["shell"]
    assert step.with_prop is None
    assert step.url == step_d["url"]
    assert step.tag == step_d["tag"]
    assert len(step.action) == 0
    assert len(step.reusable_workflow) == 0
    assert len(step.using_param) == 0


def test_composite_action_step_from_dict_run_dependency():
    step_d = {
        "run": "${{ github.action_path }}/setup_pip.ps1",
        "shell": "pwsh",
        "env": {
            "PYTHON_VERSION": "${{ steps.setup.outputs.python-version }}",
            "SETUP_PYTHON_PATH": "${{ steps.setup.outputs.python-path }}",
        },
        "_id": "f85b9778e35a1273d88c7dabdb210eaf",
        "path": "data/actions/ytdl-org|setup-python|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "tag": "v1",
    }

    step = composite_action.CompositeActionStep.from_dict(step_d)

    assert step._id == step_d["_id"]
    assert step.name is None
    assert step.path == step_d["path"]
    assert step.run == step_d["run"]
    assert step.uses is None
    assert step.ref is None
    assert step.shell == step_d["shell"]
    assert step.url == step_d["url"]
    assert step.tag == step_d["tag"]
    assert step.with_prop is None
    assert len(step.action) == 0
    assert len(step.reusable_workflow) == 0
    assert len(step.using_param) == 1


def test_composite_action_step_from_dict_using():
    step_d = {
        "uses": "actions/setup-python@bd6b4b6205c4dbad673328db7b31b7fab9e241c0",
        "id": "setup",
        "with": {
            "python-version": "${{ steps.build.outputs.python-version }}",
            "cache": "${{ inputs.cache }}",
            "architecture": "${{ steps.build.outputs.architecture }}",
            "check-latest": "${{ inputs.check-latest }}",
            "token": "${{ inputs.token }}",
            "cache-dependency-path": "${{ inputs.cache-dependency-path }}",
            "update-environment": "${{ inputs.update-environment }}",
        },
        "_id": "11e15e6b7424478c2e32fd22ed477c21",
        "path": "data/actions/ytdl-org|setup-python|action.yml",
        "url": "https://github.com/CycodeLabs/Raven/pull/1",
        "tag": "v1",
    }

    step = composite_action.CompositeActionStep.from_dict(step_d)
    assert step._id == step_d["_id"]
    assert step.name == step_d["id"]
    assert step.path == step_d["path"]
    assert step.run is None
    assert step.uses == step_d["uses"]
    assert step.ref == "bd6b4b6205c4dbad673328db7b31b7fab9e241c0"
    assert step.shell is None
    assert step.url == step_d["url"]
    assert step.tag == step_d["tag"]
    assert step.with_prop == [
        "python-version:${{ steps.build.outputs.python-version }}",
        "cache:${{ inputs.cache }}",
        "architecture:${{ steps.build.outputs.architecture }}",
        "check-latest:${{ inputs.check-latest }}",
        "token:${{ inputs.token }}",
        "cache-dependency-path:${{ inputs.cache-dependency-path }}",
        "update-environment:${{ inputs.update-environment }}",
    ]
    # Check if step.action should be == 0 or 1
    # assert len(step.action) == 0
    assert len(step.reusable_workflow) == 0
    assert len(step.using_param) == 0
