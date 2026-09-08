"""Render single prompts and guided workflows without calling an AI service."""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from string import Template
import sys


LIBRARY = Path(__file__).resolve().parents[1] / "prompts"


@dataclass
class Variable:
    question: str
    required: bool = True
    default: str = ""
    multiline: bool = False


@dataclass
class Step:
    path: Path
    instruction: str
    template: Template


def load_prompt(folder: Path) -> tuple[str, list[Step], dict[str, Variable]]:
    """Validate the entire definition before collecting any user input."""
    folder = folder.resolve()
    raw_variables = json.loads((folder / "variables.json").read_text(encoding="utf-8"))
    if not isinstance(raw_variables, dict):
        raise ValueError("variables.json must contain an object")
    variables = {}
    for name, definition in raw_variables.items():
        if not isinstance(definition, dict):
            raise ValueError(f"Invalid definition for variable {name!r}")
        if set(definition) - {"question", "required", "default", "multiline"}:
            raise ValueError(f"Unknown options for variable {name!r}")
        question = definition.get("question")
        required = definition.get("required", True)
        default = definition.get("default", "")
        multiline = definition.get("multiline", False)
        if not isinstance(question, str) or not question.strip():
            raise ValueError(f"Variable {name!r} needs a nonempty question")
        if not isinstance(required, bool) or not isinstance(multiline, bool):
            raise ValueError(f"Variable {name!r} flags must be booleans")
        if not isinstance(default, str):
            raise ValueError(f"Variable {name!r} default must be a string")
        variables[name] = Variable(question, required, default, multiline)

    workflow_path = folder / "workflow.json"
    title = folder.name
    definitions = [{"template": "prompt.md", "instruction": ""}]
    if workflow_path.exists():
        workflow = json.loads(workflow_path.read_text(encoding="utf-8"))
        if not isinstance(workflow, dict):
            raise ValueError("workflow.json must contain an object")
        title = workflow.get("title")
        definitions = workflow.get("steps")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Workflow needs a nonempty title")
        if not isinstance(definitions, list) or not definitions:
            raise ValueError("Workflow needs a nonempty steps list")

    steps = []
    used: set[str] = set()
    filenames: set[str] = set()
    for definition in definitions:
        if not isinstance(definition, dict):
            raise ValueError("Each step must be an object")
        filename = definition.get("template")
        instruction = definition.get("instruction", "")
        if not isinstance(filename, str) or not filename:
            raise ValueError("Each step needs a template path")
        if not isinstance(instruction, str):
            raise ValueError("Step instruction must be a string")
        path = (folder / filename).resolve()
        if Path(filename).is_absolute() or not path.is_relative_to(folder):
            raise ValueError(f"Template must stay inside its prompt folder: {filename}")
        if path.name in filenames:
            raise ValueError(f"Duplicate output filename: {path.name}")
        filenames.add(path.name)
        template = Template(path.read_text(encoding="utf-8"))
        if not template.template.strip() or not template.is_valid():
            raise ValueError(f"Empty template or invalid placeholder in {filename}")
        used.update(template.get_identifiers())
        steps.append(Step(path, instruction, template))
    missing = used - variables.keys()
    unused = variables.keys() - used
    if missing:
        raise ValueError(f"Missing variable definitions: {', '.join(sorted(missing))}")
    if unused:
        raise ValueError(f"Unused variable definitions: {', '.join(sorted(unused))}")
    return title, steps, variables


def ask(variable: Variable) -> str:
    while True:
        print(variable.question, file=sys.stderr)
        if variable.default:
            print(f"Default: {variable.default}", file=sys.stderr)
        if variable.multiline:
            print("Enter text; finish with a line containing only '.'", file=sys.stderr)
            lines = []
            while (line := input()) != ".":
                lines.append(line)
            answer = "\n".join(lines)
        else:
            answer = input()
        if not answer.strip():
            answer = variable.default
        if answer.strip() or not variable.required:
            return answer
        print("An answer is required. Please try again.", file=sys.stderr)


def render(folder: Path, output_dir: Path | None = None) -> None:
    title, steps, variables = load_prompt(folder)
    if output_dir is not None:
        output_dir = output_dir.resolve()
        if output_dir.is_relative_to(LIBRARY.resolve()) or output_dir.is_relative_to(folder.resolve()):
            raise ValueError("Output directory must be outside prompt sources")
        for step in steps:
            destination = output_dir / step.path.name
            if destination.exists() or destination.is_symlink():
                raise FileExistsError(f"Refusing to overwrite {destination}")
        output_dir.mkdir(parents=True, exist_ok=True)
    print(title, file=sys.stderr)
    answers: dict[str, str] = {}
    for index, step in enumerate(steps, 1):
        print(f"\nStep {index}/{len(steps)}: {step.path.stem}", file=sys.stderr)
        if step.instruction:
            print(step.instruction, file=sys.stderr)
        for name in step.template.get_identifiers():
            if name not in answers:
                answers[name] = ask(variables[name])
        text = step.template.substitute(answers)
        print(text, flush=True)
        if output_dir is not None:
            destination = output_dir / step.path.name
            # Exclusive creation also protects against files created after preflight.
            with destination.open("x", encoding="utf-8") as output:
                output.write(text)
            print(f"Saved: {destination}", file=sys.stderr)
        if index < len(steps):
            print("Run this prompt in your AI chat. Press Enter when ready for the next step.", file=sys.stderr)
            input()


def discover(root: Path = LIBRARY) -> list[Path]:
    return sorted({path.parent for pattern in ("prompt.md", "workflow.json") for path in root.rglob(pattern)})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", nargs="?", type=Path, help="Prompt or guided workflow folder")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="List prompt folders in the library")
    mode.add_argument("--check", action="store_true", help="Validate the selected folder or entire library")
    parser.add_argument("--output-dir", type=Path, help="Save rendered Markdown outside prompt sources; never overwrite")
    args = parser.parse_args()
    if args.list and args.folder:
        parser.error("--list does not accept a folder")
    if args.output_dir and (args.list or args.check):
        parser.error("--output-dir is only supported when rendering")
    if not args.list and not args.check and args.folder is None:
        parser.error("Provide a prompt folder, --list, or --check")
    try:
        if args.list:
            for folder in discover():
                print(folder.relative_to(LIBRARY.parent))
        elif args.check:
            folders = [args.folder] if args.folder else discover()
            if not folders:
                raise ValueError("No prompts found")
            for folder in folders:
                title, steps, variables = load_prompt(folder)
                print(f"OK: {title} ({len(steps)} steps, {len(variables)} variables)")
        else:
            render(args.folder, args.output_dir)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nCancelled. Completed output files, if any, were kept.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    sys.exit(main())
