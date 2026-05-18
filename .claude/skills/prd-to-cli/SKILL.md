---
name: prd-to-cli
description: Generate a Python Click CLI project from a PRD markdown file produced by `doc-to-prd`. Use this skill when a PRD must be converted into a runnable scaffold with resource commands, configuration files, batch processing, and packaging metadata.
triggers:
  - User provides a PRD markdown file and wants a Python CLI project generated from it.
  - User completed `doc-to-prd` and wants the final scaffolded project.
  - User asks to convert implementation-ready API requirements into a Click-based CLI codebase.
do_not_trigger_when:
  mode: intent
  conditions:
    - User only wants to discuss, review, or edit PRD content.
    - No PRD source is available and none can be inferred safely.
    - User wants to generate the PRD itself instead of the CLI scaffold.
---

# prd-to-cli

Generate a runnable Python Click CLI scaffold from a PRD markdown file. Use the bundled generator script and templates that already exist in this repository instead of recreating the scaffold manually.

Focus on deterministic project generation. Keep the generated output aligned with the parser and templates in `scripts/generate_cli_from_prd.py` and `assets/`.

## Expected Inputs

Accept one required PRD source and one required output directory:

```text
/prd-to-cli <PRD_FILE> <OUTPUT_DIR>
```

Interpret `PRD_FILE` as a local markdown file path containing the API PRD.

Interpret `OUTPUT_DIR` as the parent directory where the generated project folder will be created.

The generator script also accepts an optional explicit project name:

```bash
python skills/prd-to-cli/scripts/generate_cli_from_prd.py <prd_file> <output_dir> [project_name]
```

Use that explicit `project_name` argument when the PRD does not contain a reliable CLI/project name or when the user wants a specific folder/package name.

## Use Bundled Resources

Use bundled resources progressively:

- Use `scripts/generate_cli_from_prd.py` as the primary implementation path.
- Use `assets/pyproject_template.toml` for packaging metadata and console script wiring.
- Use `assets/config_template.py`, `assets/utils_template.py`, `assets/logger_template.py`, `assets/output_template.py`, `assets/test_cli_template.py`, and `assets/makefile_template.mk` as the source of truth for generated support files.
- Use `references/generated_structure.md` to understand the intended project layout.
- Use `references/input_format_specs.md` and `references/output_configuration.md` only when validating or explaining batch behavior.

Do not hand-write large generated files when the script can produce them.

## Workflow

### 1. Validate the PRD

Confirm the PRD contains enough structure for the parser in `scripts/generate_cli_from_prd.py`:

- A top-level title
- A parseable base URL such as `**Base URL:** https://...`
- An `## Implementation Decisions` section that includes `HTTP Library`
- A resource inventory line such as `**Resources:** \`users, orders\`` or explicit resource headers like `### USERS Resource`
- Endpoint inventory bullets or endpoint subsections that help map resource names to real API paths

If the PRD is missing critical parsing signals, stop and fix the PRD first instead of guessing.

### 2. Resolve the Generated Project Name

Prefer the project name in this order:
1. Explicit user-provided output name
2. Explicit generator argument `[project_name]`
3. CLI/project name recorded in the PRD
4. Safe fallback only when necessary

Normalize the generated project name so it is safe for folder names, package metadata, and console scripts.

### 3. Run the Generator Script

Generate the project with:

```bash
python skills/prd-to-cli/scripts/generate_cli_from_prd.py <prd_file> <output_dir> [project_name]
```

Treat the script output as authoritative for the initial scaffold. The current generator creates:

- `src/cli.py`
- `src/client.py`
- `src/batch_processor.py`
- `src/config.py`
- `src/logger.py`
- `src/output.py`
- `src/utils.py`
- `src/commands/*.py`
- `tests/test_cli.py`
- `.env.example`
- `requirements.txt`
- `pyproject.toml`
- `Makefile`
- `data/`
- `output/`

Do not promise files the script does not actually create.

### 4. Preserve Current Generator Semantics

Keep instructions aligned with the actual implementation:

- Resource command files currently generate `list`, `get`, and `create` commands.
- Batch processing currently accepts `.csv` and `.txt` inputs.
- Batch output supports `json`, `csv`, `xlsx`, and `sqlite` via the generated `src/output.py` helpers.
- Authentication is inferred from the PRD text and mapped to API key or bearer-token headers when detected.
- Supported HTTP client libraries are `requests`, `httpx`, `aiohttp`, and `urllib3`.

Do not describe unsupported behavior as complete.

### 5. Post-Generation Validation

After generation, validate the scaffold from the generated project root:

```bash
uv sync
uv run [cli-name] --help
uv run pytest tests/ -v
```

Then validate generated read paths by executing low-volume GET/list requests for each generated GET-style command or endpoint mapping:

- Prefer `list` commands for each generated resource group.
- Limit the requested records to a small number such as `10` whenever the API supports a limit/count/page-size style parameter.
- Use the API's documented parameter names rather than guessing, for example `--limit 10`, `--page-size 10`, or an equivalent query argument.
- If a generated resource has a direct GET-by-id path but no safe sample identifier, validate the list/read entry point instead of fabricating IDs.
- Treat this low-volume live request pass as required validation, not an optional extra.

Also run the generated `Makefile` targets when they are relevant and installed:

```bash
make help
make test
```

If dependency installation or validation fails, fix the generated project or templates before considering the task complete.

### 6. Explain Current Limitations Plainly

Surface generator limitations instead of hiding them. Important current constraints include:

- Resource parsing depends on PRD formatting discipline.
- Resource command generation is scaffold-level, not endpoint-complete.
- Batch CSV/TXT parsing is simple and does not cover every payload shape.
- `src/batch_processor.py` does not fully implement CSV/XLSX export logic yet even though those formats appear in options.
- Auth handling is generic and may need API-specific follow-up edits.

When a limitation affects the user’s target API, say so explicitly.

## PRD Contract for Reliable Generation

The upstream PRD should include these exact parseable signals whenever possible:

- `**Base URL:** https://...`
- `**HTTP Library:** requests`
- `**Resources:** \`users, orders, invoices\``
- `### USERS Resource`
- `#### 1. List Users`
- `- \`/v1/users\``

Prefer fixing the PRD to match this contract over making the parser guess.

## Output Rules

Generate one project directory under the requested output location. Ensure the result is runnable with:

```bash
uv sync
uv run [cli-name] --help
```

Keep `pyproject.toml`, `requirements.txt`, and the console script entry point consistent with the selected project name and HTTP library.

## Quality Bar

Ensure the generated project is:

- Script-generated first, manually patched only when necessary
- Consistent with the PRD decisions
- Installable with `uv`
- Wired to `uv run [cli-name]`
- Clear about any scaffold-level placeholders or incomplete endpoint coverage

## Handoff

Treat the generated directory as the final artifact for this step. If the project needs API-specific refinements after generation, make them in the generated codebase rather than rewriting the skill instructions to pretend the scaffold is more complete than it is.
