"""Exercise the offline renderer and public library without interactive input."""

import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from scripts import render_prompt as renderer


ROOT = Path(__file__).resolve().parents[1]


class RenderPromptTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.folder = self.root / "source"
        self.folder.mkdir()
        self.output = self.root / "output"
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self.enterContext(patch("sys.stdout", self.stdout))
        self.enterContext(patch("sys.stderr", self.stderr))
        self.input = self.enterContext(patch("builtins.input"))

    def fixture(self, text: str = "${context}", variables: object = None) -> None:
        if variables is None:
            variables = {"context": {"question": "Context?"}}
        (self.folder / "prompt.md").write_text(text, encoding="utf-8")
        (self.folder / "variables.json").write_text(json.dumps(variables), encoding="utf-8")

    def workflow(self) -> None:
        self.fixture("First: ${context}")
        (self.folder / "second.md").write_text("Second: $context / ${choice}", encoding="utf-8")
        (self.folder / "variables.json").write_text(json.dumps({
            "context": {"question": "Context?"},
            "choice": {"question": "Choice?"},
        }), encoding="utf-8")
        (self.folder / "workflow.json").write_text(json.dumps({
            "title": "Two stages",
            "steps": [
                {"template": "prompt.md", "instruction": "Run first"},
                {"template": "second.md", "instruction": "Run second"},
            ],
        }), encoding="utf-8")

    def main(self, *arguments: str) -> int:
        with patch("sys.argv", ["render_prompt.py", *arguments]):
            return renderer.main()

    def test_dynamic_unique_identifiers_and_literal_repeated_replacement(self) -> None:
        self.fixture("${new_42} $other ${new_42} $new_42 $$", {
            "other": {"question": "Other?"},
            "new_42": {"question": "New?"},
        })
        literal = "$5 ${other} $new_42 \\ untouched"
        self.input.side_effect = [literal, "second"]
        renderer.render(self.folder)
        self.assertEqual(self.stdout.getvalue(), f"{literal} second {literal} {literal} $\n")
        self.assertEqual(self.input.call_count, 2)
        self.assertLess(self.stderr.getvalue().index("New?"), self.stderr.getvalue().index("Other?"))

    def test_missing_unused_and_malformed_templates_fail_before_questions(self) -> None:
        for text, variables, message in [
            ("$unknown", {}, "Missing variable definitions"),
            ("literal", {"unused": {"question": "Unused?"}}, "Unused variable definitions"),
            ("${broken", {}, "invalid placeholder"),
            ("$9", {}, "invalid placeholder"),
            (" \n", {}, "Empty template"),
        ]:
            with self.subTest(text=text):
                self.fixture(text, variables)
                with self.assertRaisesRegex(ValueError, message):
                    renderer.render(self.folder)
        self.input.assert_not_called()
        self.assertEqual(self.stdout.getvalue(), "")

    def test_malformed_variable_schema(self) -> None:
        invalid = [[], "text", {"context": "question"}, {"context": {}},
                   {"context": {"question": " "}}, {"context": {"question": 1}},
                   {"context": {"question": "Q", "unknown": True}},
                   {"context": {"question": "Q", "required": 1}},
                   {"context": {"question": "Q", "multiline": "yes"}},
                   {"context": {"question": "Q", "default": None}}]
        for variables in invalid:
            with self.subTest(variables=variables):
                self.fixture(variables=variables)
                with self.assertRaises(ValueError):
                    renderer.render(self.folder)
        self.input.assert_not_called()

    def test_invalid_json_and_missing_files(self) -> None:
        self.fixture()
        (self.folder / "variables.json").write_text("{", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            renderer.render(self.folder)
        self.fixture()
        (self.folder / "prompt.md").unlink()
        with self.assertRaises(FileNotFoundError):
            renderer.render(self.folder)
        self.input.assert_not_called()

    def test_bad_workflow(self) -> None:
        self.fixture()
        invalid = [[], {}, {"title": " ", "steps": [{}]},
                   {"title": 1, "steps": [{}]}, {"title": "T", "steps": []},
                   {"title": "T", "steps": {}}, {"title": "T", "steps": [1]},
                   {"title": "T", "steps": [{}]},
                   {"title": "T", "steps": [{"template": 1}]},
                   {"title": "T", "steps": [{"template": ""}]},
                   {"title": "T", "steps": [{"template": "prompt.md", "instruction": 1}]}]
        for workflow in invalid:
            with self.subTest(workflow=workflow):
                (self.folder / "workflow.json").write_text(json.dumps(workflow), encoding="utf-8")
                with self.assertRaises(ValueError):
                    renderer.render(self.folder)
        (self.folder / "workflow.json").write_text("{", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            renderer.render(self.folder)
        self.input.assert_not_called()

    def test_template_traversal_absolute_path_and_symlink_escape(self) -> None:
        self.fixture()
        outside = self.root / "outside.md"
        outside.write_text("$context", encoding="utf-8")
        (self.folder / "escape.md").symlink_to(outside)
        for filename in ["../outside.md", str(outside), "escape.md"]:
            with self.subTest(filename=filename):
                (self.folder / "workflow.json").write_text(json.dumps({
                    "title": "Unsafe", "steps": [{"template": filename}],
                }), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "must stay inside"):
                    renderer.render(self.folder)
        self.input.assert_not_called()

    def test_duplicate_output_basenames_and_late_invalid_step(self) -> None:
        self.workflow()
        nested = self.folder / "nested"
        nested.mkdir()
        (nested / "prompt.md").write_text("$choice", encoding="utf-8")
        (self.folder / "workflow.json").write_text(json.dumps({
            "title": "Duplicate", "steps": [
                {"template": "prompt.md"}, {"template": "nested/prompt.md"},
            ],
        }), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Duplicate output filename"):
            renderer.render(self.folder)
        self.workflow()
        (self.folder / "second.md").write_text("${broken", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "invalid placeholder"):
            renderer.render(self.folder)
        self.input.assert_not_called()
        self.assertEqual(self.stdout.getvalue(), "")

    def test_required_empty_retries_defaults_optional_and_multiline(self) -> None:
        cases = [
            (renderer.Variable("Q"), ["", "  ", " answer "], " answer ", 2),
            (renderer.Variable("Q", default="fallback"), [" "], "fallback", 0),
            (renderer.Variable("Q", required=False), [""], "", 0),
            (renderer.Variable("Q", required=False), ["  "], "", 0),
            (renderer.Variable("Q", multiline=True), [".", "one", "", "$two", "."], "one\n\n$two", 1),
            (renderer.Variable("Q", default="fallback", multiline=True), ["."], "fallback", 0),
            (renderer.Variable("Q", required=False, multiline=True), ["."], "", 0),
            (renderer.Variable("Q", multiline=True), [" . ", "..", "."], " . \n..", 0),
        ]
        for variable, answers, expected, retries in cases:
            with self.subTest(variable=variable, answers=answers):
                self.input.reset_mock()
                self.input.side_effect = answers
                self.stderr.seek(0)
                self.stderr.truncate()
                self.assertEqual(renderer.ask(variable), expected)
                self.assertEqual(self.input.call_count, len(answers))
                self.assertEqual(self.stderr.getvalue().count("Please try again."), retries)
                if variable.default:
                    self.assertIn("Default: fallback", self.stderr.getvalue())
        self.assertEqual(self.stdout.getvalue(), "")

    def test_workflow_reuses_answers_and_pauses_after_output_only(self) -> None:
        self.workflow()
        snapshots: list[tuple[str, str]] = []
        answers = iter(["shared", "pause is not an answer", "selected"])

        def answer() -> str:
            snapshots.append((self.stdout.getvalue(), self.stderr.getvalue()))
            return next(answers)

        self.input.side_effect = answer
        renderer.render(self.folder)
        self.assertEqual(self.stdout.getvalue(), "First: shared\nSecond: shared / selected\n")
        self.assertEqual(len(snapshots), 3)
        self.assertEqual(snapshots[0][0], "")
        self.assertEqual(snapshots[1][0], "First: shared\n")
        self.assertNotIn("Choice?", snapshots[1][1])
        self.assertIn("Run second\nChoice?", snapshots[2][1])
        self.assertEqual(self.stderr.getvalue().count("Context?"), 1)
        self.assertEqual(self.stderr.getvalue().count("Press Enter when ready"), 1)

    def test_completed_output_files_match_stdout(self) -> None:
        self.workflow()
        self.input.side_effect = ["shared", "", "chosen"]
        renderer.render(self.folder, self.output)
        self.assertEqual((self.output / "prompt.md").read_text(), "First: shared")
        self.assertEqual((self.output / "second.md").read_text(), "Second: shared / chosen")
        self.assertEqual(self.stdout.getvalue(), "First: shared\nSecond: shared / chosen\n")
        self.assertEqual(self.stderr.getvalue().count("Saved:"), 2)

    def test_existing_later_output_refused_before_questions(self) -> None:
        self.workflow()
        self.output.mkdir()
        existing = self.output / "second.md"
        existing.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            renderer.render(self.folder, self.output)
        self.assertEqual(existing.read_text(), "keep")
        self.assertFalse((self.output / "prompt.md").exists())
        self.input.assert_not_called()
        self.assertEqual(self.stdout.getvalue(), "")

    def test_dangling_output_symlink_refused(self) -> None:
        self.fixture()
        self.output.mkdir()
        target = self.root / "missing"
        (self.output / "prompt.md").symlink_to(target)
        with self.assertRaises(FileExistsError):
            renderer.render(self.folder, self.output)
        self.assertFalse(target.exists())
        self.input.assert_not_called()

    def test_output_exclusive_creation_protects_against_race(self) -> None:
        self.fixture()

        def answer() -> str:
            (self.output / "prompt.md").write_text("racing writer", encoding="utf-8")
            return "answer"

        self.input.side_effect = answer
        with self.assertRaises(FileExistsError):
            renderer.render(self.folder, self.output)
        self.assertEqual((self.output / "prompt.md").read_text(), "racing writer")

    def test_output_cannot_target_sources_including_symlink(self) -> None:
        self.fixture()
        alias = self.root / "alias"
        alias.symlink_to(self.folder, target_is_directory=True)
        for destination in [self.folder, self.folder / "new", alias / "new", renderer.LIBRARY / "new"]:
            with self.subTest(destination=destination):
                with self.assertRaisesRegex(ValueError, "outside prompt sources"):
                    renderer.render(self.folder, destination)
        self.input.assert_not_called()

    def test_main_cancellation_preserves_completed_files(self) -> None:
        self.workflow()
        for error in [EOFError, KeyboardInterrupt]:
            for during in ["question", "pause", "later question"]:
                with self.subTest(error=error, during=during):
                    output = self.root / f"{error.__name__}-{during}"
                    self.input.side_effect = {
                        "question": [error()], "pause": ["shared", error()],
                        "later question": ["shared", "", error()],
                    }[during]
                    self.assertEqual(self.main(str(self.folder), "--output-dir", str(output)), 130)
                    self.assertIn("Cancelled.", self.stderr.getvalue())
                    self.assertFalse((output / "second.md").exists())
                    if during != "question":
                        self.assertEqual((output / "prompt.md").read_text(), "First: shared")
                    else:
                        self.assertFalse((output / "prompt.md").exists())

    def test_main_error_returns(self) -> None:
        self.assertEqual(self.main(str(self.folder)), 1)
        self.fixture("$missing", {})
        self.assertEqual(self.main(str(self.folder)), 1)
        self.assertIn("Error:", self.stderr.getvalue())
        with patch.object(renderer, "discover", return_value=[]):
            self.assertEqual(self.main("--check"), 1)
        self.assertIn("No prompts found", self.stderr.getvalue())
        self.input.assert_not_called()

    def test_main_invalid_argument_combinations(self) -> None:
        for arguments in [[], ["--list", str(self.folder)], ["--list", "--check"],
                          ["--check", "--output-dir", str(self.output)],
                          ["--list", "--output-dir", str(self.output)]]:
            with self.subTest(arguments=arguments):
                with self.assertRaises(SystemExit) as raised:
                    self.main(*arguments)
                self.assertEqual(raised.exception.code, 2)
        self.input.assert_not_called()

    def test_discover_unique_sorted_single_and_workflow_folders(self) -> None:
        self.workflow()
        other = self.root / "aaa"
        other.mkdir()
        (other / "prompt.md").write_text("constant", encoding="utf-8")
        self.assertEqual(renderer.discover(self.root), [other, self.folder])

    def test_list_and_check_real_library_without_questions(self) -> None:
        folders = renderer.discover()
        self.assertTrue(folders)
        self.assertEqual(self.main("--list"), 0)
        self.assertEqual(self.stdout.getvalue().splitlines(), [str(p.relative_to(ROOT)) for p in folders])
        self.stdout.seek(0)
        self.stdout.truncate()
        self.assertEqual(self.main("--check"), 0)
        self.assertEqual(len(self.stdout.getvalue().splitlines()), len(folders))
        for folder in folders:
            self.assertEqual(self.main("--check", str(folder)), 0)
        self.input.assert_not_called()
        self.assertEqual(self.stderr.getvalue(), "")

    def test_real_library_all_steps_render_with_dynamic_inputs_and_pauses(self) -> None:
        folders = renderer.discover()
        self.assertTrue(folders)
        for index, folder in enumerate(folders):
            with self.subTest(folder=folder):
                title, steps, variables = renderer.load_prompt(folder)
                answers: dict[str, str] = {}
                inputs: list[str] = []
                expected: list[str] = []
                for step_index, step in enumerate(steps):
                    for name in step.template.get_identifiers():
                        if name not in answers:
                            value = f"Answer for {name}: $42 ${{literal}}"
                            inputs.append(value)
                            if variables[name].multiline:
                                inputs.extend(["Second line", "."])
                                value += "\nSecond line"
                            answers[name] = value
                    expected.append(step.template.substitute(answers))
                    if step_index < len(steps) - 1:
                        inputs.append("")
                self.stdout.seek(0)
                self.stdout.truncate()
                self.stderr.seek(0)
                self.stderr.truncate()
                self.input.reset_mock()
                self.input.side_effect = inputs
                output = self.root / f"library-{index}"
                self.assertEqual(self.main(str(folder), "--output-dir", str(output)), 0)
                self.assertEqual(self.stdout.getvalue(), "".join(text + "\n" for text in expected))
                self.assertEqual(self.input.call_count, len(inputs))
                self.assertIn(title, self.stderr.getvalue())
                self.assertEqual(self.stderr.getvalue().count("Press Enter when ready"), len(steps) - 1)
                self.assertEqual(set(answers), set(variables))
                for step, text in zip(steps, expected):
                    self.assertEqual((output / step.path.name).read_text(encoding="utf-8"), text)
                for variable in variables.values():
                    self.assertEqual(self.stderr.getvalue().count(variable.question), 1)


class DocumentationTests(unittest.TestCase):
    def test_public_markdown_relative_links_exist(self) -> None:
        # Explicit public roots avoid private scripts, generated output, and virtualenvs.
        documents = list(ROOT.glob("*.md"))
        for name in ("prompts", "docs", ".github"):
            documents.extend((ROOT / name).rglob("*.md"))
        checked = 0
        for document in documents:
            text = document.read_text(encoding="utf-8")
            text = re.sub(r"```.*?```|~~~.*?~~~", "", text, flags=re.DOTALL)
            targets = re.findall(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)", text)
            targets += re.findall(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, flags=re.MULTILINE)
            for target in targets:
                url = urlsplit(target.strip("<>"))
                if url.scheme or url.netloc or not url.path or url.path.startswith("/"):
                    continue
                with self.subTest(document=document.relative_to(ROOT), target=target):
                    destination = (document.parent / unquote(url.path)).resolve()
                    self.assertTrue(destination.is_relative_to(ROOT), "Link escapes repository")
                    self.assertTrue(destination.exists(), f"Broken relative link: {target}")
                checked += 1
        self.assertGreater(checked, 0)


if __name__ == "__main__":
    unittest.main()
