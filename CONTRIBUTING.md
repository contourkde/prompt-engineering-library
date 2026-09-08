# Contributing

## Add a Prompt

1. Choose a topic and a descriptive `snake_case` folder name under `prompts/`.
2. Add `README.md` explaining purpose, intended users, inputs, expected output,
   usage, and limitations. Link it from the topic and root catalogs.
3. For a single-stage prompt, add `prompt.md` and `variables.json` in that folder.
   For a guided variant, add a `guided/` folder with its own README, variable
   definitions, workflow definition, and `steps/` templates.
4. Add `example.md` with fictional or explicitly authorized data and clear
   separation between user-supplied assumptions and verified facts.
5. Run validation, tests, and type checking before opening a pull request.

Do not add a custom Python script for each prompt. The shared renderer discovers
variables from templates. Add application logic only when an actual reusable
requirement cannot be expressed by the existing format.

## Template Format

```markdown
Act as ${persona}.
Explain ${topic} to ${audience}.
Return three concise bullet points.
```

Use `${snake_case}` placeholders consistently. Fixed instructions do not need
variables. Use `$$` for a literal dollar sign in template text. Templates are
plain text, not Python or Jinja; conditionals, loops, and includes are unsupported.

`variables.json` maps every unique variable to its question definition:

```json
{
  "persona": {
    "question": "What role should the AI adopt?",
    "default": "patient teacher",
    "required": true
  },
  "topic": {"question": "What topic should be explained?", "required": true},
  "audience": {"question": "Who is the audience?", "required": true}
}
```

Supported options: nonempty `question`, boolean `required` (default `true`),
string `default` (default empty), and boolean `multiline` (default `false`).
Unknown options, missing definitions, unused definitions, and malformed templates
fail validation. Optional blank inputs become empty strings. Repeated variables
are asked once per run in first-appearance order.

## Guided Workflows

`workflow.json` declares a title and an ordered, nonempty list of steps:

```json
{
  "title": "Example Guided Workflow",
  "steps": [
    {"template": "steps/01_draft.md", "instruction": "Describe your goal."},
    {"template": "steps/02_refine.md", "instruction": "Provide the draft from your AI chat."}
  ]
}
```

Paths must be relative and remain inside the workflow folder, including symlink
resolution. Step basenames must be unique because saved output uses those names.
If `workflow.json` exists it takes precedence over `prompt.md`; do not put both
formats in one folder. All steps are validated before any questions are asked.
Definitions may be shared across steps but must be used somewhere in the workflow.

Instructions appear before that step's questions. After each nonfinal prompt,
the renderer pauses for the user to run it in an external AI chat. Downstream
choices, such as a selected structure, must be explicit inputs. Include enough
shared context in each template to support a fresh chat; never assume the AI
remembers a previous session. See the
[guided presentation example](prompts/presentations/presentation_deck_architect/guided/README.md).

## Quality Checks

```bash
uv sync --locked
uv run python scripts/render_prompt.py --check
uv run python -m unittest discover -s tests -v
uv run ty check
```

Use uv for project management and ty for type checking. Keep changes focused and
add tests when changing renderer behavior. Record revisions through Git, not
duplicate `v1`/`v2` template folders. Label unsupported claims `UNVERIFIED`, require
source dates where relevant, and never invent statistics or citations.

Before staging, inspect `git status` and your diff. Never force-add ignored local
scripts, environment files, generated prompts, or real credentials. Follow
[SECURITY.md](SECURITY.md) for suspected exposures. If adapting external prompts,
check their license and preserve required attribution.
