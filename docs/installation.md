# Installation

Install the project dependencies with `uv`:

```bash
make install
```

For editable development installs:

```bash
make install-dev
```

To build or serve this documentation:

```bash
make install-docs
make docs-build
make docs-serve
```

The documentation extra uses `mkdocs-click`, which currently requires Python 3.9 or newer. The CLI runtime still supports the Python version range declared in `pyproject.toml`.

The CLI entrypoint is:

```bash
uv run courtlistener-cli --help
```
