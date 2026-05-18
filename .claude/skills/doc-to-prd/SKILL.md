---
name: doc-to-prd
description: Create a comprehensive `{project_name}_PRD.md` for a Python API CLI from an OpenAPI spec or API documentation. Use this skill after `api-to-doc` or whenever an API spec/docs must be converted into an implementation-ready PRD for `prd-to-cli`.
triggers:
  - User provides an OpenAPI/Swagger file, API docs URL, or local API documentation and wants a PRD artifact.
  - User asks to convert API documentation into implementation-ready requirements for a Python CLI.
  - User completed `api-to-doc` and needs the next workflow artifact before `prd-to-cli`.
do_not_trigger_when:
  mode: intent
  conditions:
    - User only wants explanation, review, or brainstorming rather than PRD generation.
    - User already has a PRD and wants code generation instead (use `prd-to-cli`).
    - No API source is available and no reliable source can be inferred.
---

# doc-to-prd

Create a single markdown artifact named `{project_name}_PRD.md` from an OpenAPI spec, Swagger file, or API documentation. Produce a PRD that is specific enough for `prd-to-cli` to generate a Python Click CLI without re-asking core implementation questions.

Keep the skill focused on requirements and interface design. Do not generate application code, tests, CI files, or deployment assets in this step.

## Expected Inputs

Accept one required source input and one optional output path:

```text
/doc-to-prd <API_SOURCE> [OUTPUT_PATH]
```

Interpret `API_SOURCE` as one of:
- Local OpenAPI YAML or JSON file
- URL to OpenAPI/Swagger JSON or YAML
- Local markdown or HTML documentation
- Documentation URL when structured API docs are the only available source

Interpret `OUTPUT_PATH` as one of:
- Exact markdown filename
- Output directory for `{project_name}_PRD.md`
- Omitted, meaning write `{project_name}_PRD.md` in the current working directory

## Use Bundled Resources

Use bundled resources progressively instead of reproducing them from memory:

- Use `references/PRD_template.md` as the canonical section layout and placeholder inventory.
- Use `assets/questions.md` as the canonical decision questionnaire.
- Treat `templates/Makefile_sample` as reference material for expected workflow conventions only.
- Treat `templates/default_config.json` as reference material for configuration fields that are common in generated CLIs.

Do not copy bundled reference material verbatim into the PRD unless it is relevant to the API being documented.

## Workflow

### 1. Validate the Source

Confirm that the provided source contains enough information to describe:
- Base URL or environment-specific base URLs
- Authentication method
- Endpoint/resource inventory
- Request parameters or payload shape
- Response shape or representative examples

If the source is incomplete, continue with the available facts, clearly mark gaps, and avoid inventing endpoint behavior.

### 2. Resolve `project_name`

Infer `project_name` from the source when possible, preferring:
1. OpenAPI `info.title`
2. Product/service title in docs
3. Prominent heading or brand name tightly coupled to the API

Normalize the result into a filesystem-safe slug:
- Lowercase
- Replace spaces and punctuation with `_`
- Remove duplicate separators

If no confident name can be inferred, ask the user for the project name before writing the file.

### 3. Capture Implementation Decisions

Use `assets/questions.md` as the canonical questionnaire. Capture the answers in the generated PRD under an `## Implementation Decisions` section.

Record decisions using the exact block shape defined in `assets/questions.md`, preserving these fields:
- `CLI Name`
- `Python Version`
- `HTTP Library`
- `Authentication`
- `Credentials Configuration`
- `Timeout`
- `Retry Policy`
- `Output Formats`
- `Output Accepted Formats and Default`
- `Batch Input Formats`
- `Default Save Data Mode`
- `Lint/Format Toolchain`

Do not ask the user to choose the authentication scheme when the API source already documents it. Record `Authentication` from the OpenAPI spec or API documentation and only ask about implementation choices that remain ambiguous, such as credential source preferences. Always record `Lint/Format Toolchain` as `ruff check --fix` + `ruff format` rather than asking the user to choose it. Do not ask the user to define validation commands in the PRD; downstream validation belongs to `prd-to-cli`. When the user has not provided preferences, ask only the minimum set of questions needed to avoid ambiguous downstream generation. Prefer recommended defaults from `assets/questions.md` when the user delegates the choice.

### 4. Write the PRD

Use `references/PRD_template.md` as the base structure. Fill it with API-specific content and keep placeholders only where the source is genuinely incomplete.

At minimum, produce:
- A top-level title naming the API/client
- Introduction and purpose
- Implementation decisions
- Installation expectations
- Configuration strategy
- Authentication requirements
- Endpoint reference
- Input/output examples
- Error handling expectations
- Logging expectations
- Validation requirements
- Makefile/project-management expectations

### 5. Preserve Downstream Parsing Signals

Write the PRD so `prd-to-cli` can parse it reliably. Include these signals whenever the source supports them:

- A base URL line in a parseable form such as `**Base URL:** https://...` or `**Base URL:** \`https://...\``
- A resource inventory line such as `**Resources:** \`users, orders, invoices\``
- Explicit resource sections in the form `### USERS Resource`
- Endpoint subsections in the form `#### 1. List Users`
- Endpoint inventory bullets with concrete paths such as `- \`/v1/users\``
- An `## Implementation Decisions` section with an explicit `HTTP Library` line

Prefer exact API paths over guessed resource names. If the docs expose `/v1/air-quality`, keep that exact path instead of simplifying it to `/airquality`.

### 6. Keep the PRD Implementation-Ready

Translate the source into decisions and constraints that matter for generation:
- Authentication headers, tokens, or query parameters
- Required environment variables
- Pagination behavior
- Rate limiting and retry expectations
- Batch input support and output format expectations
- Error categories and likely failure modes
- Resource naming that maps cleanly to CLI command groups

Always include a downstream validation requirement in the PRD stating that `prd-to-cli` must perform low-volume live validation for generated GET/list paths. This requirement should direct the generated project to execute read/list commands with a small record cap such as `10`, using the API's documented pagination or limit parameter names whenever available.

If the source lacks a detail that affects implementation, state the assumption explicitly in the PRD instead of silently filling the gap.

## Output Rules

Write exactly one primary artifact:
- `{project_name}_PRD.md`

Avoid generating adjacent implementation files at this step. Reference sample config or Makefile conventions in prose when helpful, but leave concrete project scaffolding to `prd-to-cli`.

## Quality Bar

Ensure the generated PRD is:
- Grounded in the provided source
- Specific enough for deterministic CLI generation
- Consistent with `uv run [cli-name] ...` workflow conventions
- Free of invented endpoints, parameters, or auth schemes
- Clear about assumptions, omissions, and unresolved questions

## Handoff

After writing `{project_name}_PRD.md`, treat it as the handoff artifact for:

```text
/prd-to-cli @{project_name}_PRD.md <output-directory>
```

If the source material is too weak to support a reliable PRD, say so plainly and identify the missing information that blocks the next step.
