# Contributing

We encourage contributions from the community to help improve our tooling and research. We manage contributions primarily through GitHub Issues and Pull Requests.

If you have a feature request, bug report, or any improvement suggestions, please create an issue to discuss it. To start contributing, you may check [good first issue](https://github.com/CycodeLabs/Raven/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) label to get started quickly into the code base.

To contribute code changes, fork our repository, make your modifications, and then submit a pull request.

## Development

To prepare a development environment, follow these instructions:

**Step 1**: Clone the project

```bash
git clone https://github.com/CycodeLabs/raven.git
cd raven
```

**Step 2**: Create a virtual environment and install requirements

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

**Step 3**: Make code modifications

**Step 4**: Setup the Redis server and the Neo4j database

```bash
make setup
```

**Step 5**: Run Raven

```bash
python3 main.py -h
```

**Step 6**: Test Raven

```bash
make test-build
```

Feel free to reach out to the development team through research@cycode.com. We appreciate your collaboration and look forward to your valuable contributions!
