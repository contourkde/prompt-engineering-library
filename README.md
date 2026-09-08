# Prompt Engineering Library

A topic-organized collection of reusable prompts with documented inputs, worked
examples, and guided workflows. An interactive, offline Python renderer fills
templates with your answers, producing Markdown ready for your preferred AI tool.
It does not call an AI service or generate presentation files itself.

## Quick Start

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run from
the repository root. Python 3.11 or newer is required; uv can provision Python.

```bash
uv sync --locked
uv run python scripts/render_prompt.py --list
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided
```

Answer the terminal questions, run each generated prompt in your AI chat, then
return to continue. Shared answers are reused during the current run. Multiline
answers end with a line containing only `.`. Blank answers accept displayed
defaults; required answers without defaults are requested again.

To save each completed step as well as print it:

```bash
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided --output-dir generated/my-deck
```

Output files are never overwritten. Choose a new output directory for each run.
Output inside prompt source folders is rejected. Cancelling preserves completed
files, but answers are not persisted and there is no resume feature. Questions and
status go to stderr; rendered Markdown goes to stdout.

## Catalog

| Topic | Prompt | Purpose |
| --- | --- | --- |
| [Presentations](prompts/presentations/README.md) | [Presentation Deck Architect](prompts/presentations/presentation_deck_architect/README.md) | Build a structure, hook, opening, and slide outline using the Persona, Task, Format, Context (PTFC) framework. |

See the [prompt catalog](prompts/README.md) and
[contribution guide](CONTRIBUTING.md) to add more prompts without changing Python.

## Repository Structure

```text
prompts/<topic>/<prompt-name>/         Prompt documentation and templates
prompts/<topic>/<prompt-name>/guided/  Multi-step variant, when needed
scripts/render_prompt.py              Shared interactive renderer
tests/                                Standard-library unittest suite
.github/workflows/ci.yml               Tests, type checks, and secret scanners
generated/                            Ignored local output
```

Single-stage prompts use `prompt.md` and `variables.json`. Guided workflows use
`workflow.json`, `variables.json`, and `steps/*.md`. Templates declare variables
with `${name}`; Python discovers unique names dynamically. Question definitions
provide labels, defaults, and validation flags. Neither prompt count nor question
count is hardcoded. Literal dollar signs in templates must be escaped as `$$`;
answers are substituted literally, never executed or recursively expanded.

## Development

[uv](https://docs.astral.sh/uv/) manages Python and the locked development
environment. [ty](https://docs.astral.sh/ty/) checks Python types. The renderer has
no third-party runtime dependencies.

```bash
uv sync --locked
uv run python -m unittest discover -s tests -v
uv run ty check
uv run python scripts/render_prompt.py --check
```

CI runs these checks on Python 3.11, 3.12, and 3.13. Commit `uv.lock` when changing
dependencies. Git history tracks prompt revisions; avoid numbered copies of the
same template merely to preserve old edits.

## Reliability and Privacy

Examples are illustrative, not verified research. Prompts require sources and
dates for factual claims and explicit `UNVERIFIED` labels where evidence is
unavailable. Model knowledge cutoffs and requested timeframes do not establish
accuracy. Review generated content before presenting or publishing it.

`personal_scripts/`, `.env` and `.env.*` files, and `generated/` are ignored.
Do not put credentials or confidential context in committed examples. Information
you paste into an external AI tool is subject to that tool's data-handling terms.
CI uses TruffleHog and Gitleaks; see [SECURITY.md](SECURITY.md) for coverage,
verification behavior, reporting, and limitations.

## Related Projects

- [Fabric](https://github.com/danielmiessler/Fabric): reusable task-based prompt patterns and AI tooling.
- [prompts.chat](https://github.com/f/prompts.chat): community prompt discovery and sharing.

This library focuses on small, transparent templates and guided user input rather
than hosting models or operating a prompt-sharing platform.
