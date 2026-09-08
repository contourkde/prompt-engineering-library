# Guided Presentation Deck Architect

Build a presentation through four prompts. You run each prompt in an AI chat, review its response, and carry selected text into the next stage. No model API, response capture, persistence, or resume is involved.

## Run

```sh
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided
uv run python scripts/render_prompt.py prompts/presentations/presentation_deck_architect/guided --output-dir generated/my-deck
```

These commands use the repository's renderer described in the [library interface](../../../README.md). Use `uv run python scripts/render_prompt.py --list` to discover workflows and `uv run python scripts/render_prompt.py --check` to validate library assets.

Before collecting answers, the renderer validates the workflow, variable definitions, and all templates. It displays each stage's instruction before asking for that stage's inputs. Shared answers are collected once and reused in memory. Multiline answers end when you enter a line containing only `.`. Empty input accepts an available default; required answers that remain empty are requested again.

The renderer prints a completed prompt at each stage. After each of the first three prompts is printed, run it in your AI chat, then press Enter at the terminal's between-step pause. The renderer exits after printing the final prompt, without another pause; run that prompt in your AI chat as well. Copy the selected response text into the next stage's questions, not merely an option number. Each prompt repeats `persona`, `topic`, `objective`, and `audience`, so it does not depend on earlier chat history.

With `--output-dir`, the renderer also creates `01_structure.md`, `02_hook.md`, `03_opening.md`, and `04_slides.md` in the requested directory, which must be outside the prompt sources. It checks all output filenames before collecting inputs, and exclusive creation also prevents overwriting files at write time. Use a new output directory for another run. Output files contain your supplied context; review them before sharing.

## Stages

The workflow defines 14 variables across four stages.

| Stage | New inputs | Fixed task |
| --- | --- | --- |
| 1. Structure | `persona`, `topic`, `objective`, `audience` | Brainstorm three distinct Beginning/Middle/End structures and recommend one. |
| 2. Hook | `chosen_structure`, `hook_context` | Propose three hooks suited to the selected structure and assess their evidence needs. |
| 3. Opening | `selected_hook`, `tone_start`, `tone_end` | Write three approximately 60-second opening options ranging between the requested tones. |
| 4. Slides | `selected_opening`, `timeframe`, `presentation_duration`, `fast_changing_subtopic`, `current_context` | Produce slide titles, 3-4 supporting bullets per slide, and speaker notes, followed by timing and evidence checks. |

Stage 4 reuses the full selected structure and hook collected earlier. The tone controls affect the opening; the selected opening carries those choices into the slide plan. For `timeframe`, provide the factual relevance period, such as `Q3 2026`, not the length of the talk. For `presentation_duration`, provide the talk duration and any Q&A allocation. For `current_context`, include the intended delivery date and available source titles, URLs or document identifiers, publication/update dates, and relevant excerpts. Evidence must support claims for the requested relevance period; a later delivery date does not change that scope. Do not enter secrets or confidential infrastructure details.

## Evidence Rules

Factual claims require a source and date. If evidence is unavailable, the prompts require `UNVERIFIED` and a nonnumeric fallback. A model's training cutoff is not evidence, and the model must not claim it browsed, tested, or verified anything it did not actually check.

An unsupported "95% downtime" claim must not be used. Prefer a nonnumeric hook about unexpected configuration drift. Broadcom/VMware migration examples are illustrative unless supporting evidence is supplied and checked. API rate limits must not be assumed; the model must identify the specific product, version, and documentation needed to establish them.

See the [worked example](example.md), [workflow manifest](workflow.json), and [variable definitions](variables.json). Return to [Presentation Deck Architect](../README.md).
