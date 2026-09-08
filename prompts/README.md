# Prompt Library

This library contains reusable prompt assets and guided workflows for use in an AI chat. Templates keep the task and output format fixed while collecting the context needed for each stage.

## Browse

- [Presentations](presentations/README.md): develop presentation narratives, openings, and slide plans.
- [Presentation Deck Architect](presentations/presentation_deck_architect/README.md): turn a presentation brief into a structured deck through four guided stages.

## Renderer Interface

Run workflows with the repository's command-line renderer:

```sh
uv run python scripts/render_prompt.py --list
uv run python scripts/render_prompt.py --check
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided --output-dir generated/my-deck
```

`--list` lists library workflows. `--check` validates library assets without collecting answers. Rendering prevalidates all assets before asking questions, then processes stages sequentially. Each stage's instructions appear before its input questions. Answers are reused in memory during that run; no persistence or resume is supported.

The renderer prints each prompt for manual use in an AI chat. Between stages, it pauses after printing the prompt: run that prompt in the chat, then press Enter in the terminal to continue. There is no pause after the final prompt. It does not call a model API or automatically capture model responses. Later questions ask you to paste your selected outputs from earlier stages.

For multiline input, enter a line containing only `.` to finish. Required empty answers are retried. Where a default is offered, empty input accepts that default. With `--output-dir`, each rendered prompt is also written using its template filename, such as `01_structure.md`. Files are created exclusively; existing files are never overwritten.

Output directories must be outside the prompt library and the selected prompt's source directory. The renderer checks for existing output filenames before collecting inputs and also uses exclusive creation when writing each file.

## Asset Contract

Each workflow directory contains `README.md`, `workflow.json`, `variables.json`, `example.md`, and its templates. `workflow.json` is an object with a string `title` and an ordered `steps` list. Each step has a relative `template` path and a string `instruction`.

`variables.json` maps variable names to objects containing a nonempty string `question` and boolean `required`. Optional `default` values are strings; optional `multiline` values are booleans. Templates use Python `string.Template` placeholders, such as `${topic}`. Literal dollar signs in templates must be escaped as `$$`. Every placeholder must have a definition, and every definition must be used in at least one workflow template.
