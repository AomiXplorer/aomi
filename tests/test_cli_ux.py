"""Tests for the installer, the interactive commands and the packaging contract.

These are behavioural on purpose: each one drives the command the way a person
or a CI job would, and checks what ends up on disk.
"""
from __future__ import annotations

import io
import json
import os
import pathlib
import re
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
FIXTURES = HERE / "fixtures"
sys.path.insert(0, str(ROOT))

from aomi import adapters, cli, configcmd, engine, initcmd, installer, paths, ui  # noqa: E402

METHODS = ("install", "update", "uninstall", "init", "audit", "contrast",
           "parity", "doctor", "config", "agents")


def run(argv):
    """Run the real entry point, returning (code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = cli.main(argv)
        except SystemExit as exc:  # argparse handles --version and usage errors
            code = exc.code if isinstance(exc.code, int) else 2
    return code, out.getvalue(), err.getvalue()


class SurfaceTest(unittest.TestCase):
    def test_version(self):
        code, out, _ = run(["--version"])
        self.assertEqual(code, 0)
        self.assertIn("aomi 1.1.0", out)

    def test_no_arguments_prints_three_commands_and_exits_clean(self):
        code, out, _ = run([])
        self.assertEqual(code, 0)
        self.assertIn("aomi install", out)
        self.assertIn("aomi --help", out)

    def test_help_lists_every_command(self):
        _, out, _ = run(["--help"])
        for name in METHODS:
            self.assertIn(name, out, f"{name} missing from --help")

    def test_a_typo_gets_a_suggestion_and_exit_two(self):
        code, _, err = run(["instal"])
        self.assertEqual(code, 2)
        self.assertIn("did you mean `aomi install`", err)

    def test_unknown_flag_exits_two_with_a_pointer(self):
        code, _, err = run(["audit", "--nope"])
        self.assertEqual(code, 2)
        self.assertIn("aomi --help", err)


class AdapterTest(unittest.TestCase):
    def test_every_adapter_documents_where_its_path_came_from(self):
        for adapter in adapters.ADAPTERS:
            self.assertTrue(adapter.docs.startswith("https://"), adapter.key)
            self.assertTrue(adapter.project and "/" in adapter.project, adapter.key)

    def test_six_named_agents_plus_the_shared_folder(self):
        labels = [adapter.key for adapter in adapters.ADAPTERS]
        for key in ("claude", "opencode", "cursor", "windsurf", "copilot", "codex", "agents"):
            self.assertIn(key, labels)

    def test_unverified_adapters_say_so(self):
        for adapter in adapters.ADAPTERS:
            if not adapter.verified:
                self.assertTrue(adapter.note, f"{adapter.key} claims nothing but explains nothing")

    def test_aliases_resolve(self):
        self.assertEqual(adapters.lookup("claude-code").key, "claude")
        self.assertEqual(adapters.lookup("devin").key, "windsurf")
        self.assertIsNone(adapters.lookup("nonexistent"))

    def test_menu_numbers_resolve(self):
        self.assertEqual(adapters.from_number("1"), adapters.ADAPTERS[0])
        self.assertIsNone(adapters.from_number("99"))

    def test_detection_reads_the_project_then_the_home(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            (cwd / ".claude").mkdir()
            found = {adapter.key for adapter, _ in adapters.detect(cwd, home)}
        self.assertIn("claude", found)
        self.assertNotIn("cursor", found)

    def test_a_global_path_missing_is_an_error_not_a_silent_guess(self):
        copilot = adapters.BY_KEY["copilot"]
        with self.assertRaises(ValueError):
            copilot.path_for("global", pathlib.Path("."), pathlib.Path.home())


class InstallTest(unittest.TestCase):
    def _install(self, adapter_key="claude", **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            adapter = adapters.BY_KEY[adapter_key]
            target = adapter.path_for("project", cwd, home)
            report = installer.install(adapter, target, **kwargs)
            yield report, target

    def test_each_adapter_installs_a_usable_skill(self):
        for adapter in adapters.ADAPTERS:
            with tempfile.TemporaryDirectory() as tmp:
                cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
                home.mkdir()
                target = adapter.path_for("project", cwd, home)
                report = installer.install(adapter, target)
                self.assertEqual(report["problems"], [], f"{adapter.key}: {report['problems']}")
                self.assertTrue((target / "SKILL.md").is_file(), adapter.key)
                self.assertTrue((target / "core" / "workflow.md").is_file(), adapter.key)
                self.assertEqual(installer.verify(target), [], adapter.key)

    def test_development_files_never_copied(self):
        for report, target in self._install():
            rel = {p.relative_to(target).as_posix() for p in target.rglob("*")}
        self.assertFalse([r for r in rel if r.startswith("tests/") or r.startswith(".git/")])
        self.assertNotIn("pyproject.toml", rel)
        self.assertNotIn("setup.py", rel)
        self.assertNotIn("aomi/cli.py", rel)

    def test_the_run_wrapper_stays_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            target = adapters.BY_KEY["agents"].path_for("project", cwd, home)
            installer.install(adapters.BY_KEY["agents"], target)
            wrapper = target / "scripts" / "run.sh"
            self.assertTrue(wrapper.is_file())
            self.assertTrue(os.access(wrapper, os.X_OK), "a runner may exec the wrapper directly")

    def test_install_twice_updates_in_place_without_nesting(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            adapter = adapters.BY_KEY["claude"]
            target = adapter.path_for("project", cwd, home)
            first = installer.install(adapter, target)
            second = installer.install(adapter, target)
            self.assertEqual(first["action"], "installed")
            self.assertEqual(second["action"], "updated")
            self.assertEqual(first["files"], second["files"])
            self.assertFalse((target / "aomi").exists(), "an update must not nest a second copy")

    def test_update_restores_a_modified_file_and_prunes_stale_ones(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            adapter = adapters.BY_KEY["cursor"]
            target = adapter.path_for("project", cwd, home)
            installer.install(adapter, target)
            (target / "SKILL.md").write_text("edited by hand\n")
            (target / "core" / "gone.md").write_text("stale\n")
            report = installer.install(adapter, target)
            self.assertNotEqual((target / "SKILL.md").read_text(), "edited by hand\n")
            self.assertFalse((target / "core" / "gone.md").exists())
            self.assertEqual(report["removed"], 1)

    def test_a_foreign_folder_is_refused_unless_forced(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            target = adapters.BY_KEY["claude"].path_for("project", cwd, home)
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("---\nname: something-else\n---\n")
            refused = installer.install(adapters.BY_KEY["claude"], target)
            self.assertEqual(refused["action"], "refused")
            self.assertTrue((target / "SKILL.md").read_text().startswith("---\nname: something-else"))
            forced = installer.install(adapters.BY_KEY["claude"], target, force=True)
            self.assertEqual(forced["action"], "updated")

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            target = adapters.BY_KEY["codex"].path_for("project", cwd, home)
            report = installer.install(adapters.BY_KEY["codex"], target, dry_run=True)
            self.assertEqual(report["action"], "dry-run")
            self.assertFalse(target.exists())
            self.assertGreater(report["files"], 30)

    def test_uninstall_removes_only_an_aomi_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            adapter = adapters.BY_KEY["opencode"]
            target = adapter.path_for("project", cwd, home)
            installer.install(adapter, target)
            self.assertEqual(installer.uninstall(target)["action"], "removed")
            self.assertFalse(target.exists())
            self.assertEqual(installer.uninstall(target)["action"], "absent")

            foreign = cwd / "someone-elses"
            foreign.mkdir()
            (foreign / "SKILL.md").write_text("---\nname: not-aomi\n---\n")
            self.assertEqual(installer.uninstall(foreign)["action"], "refused")
            self.assertTrue(foreign.exists())

    def test_a_directory_needs_no_agent_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "somewhere" / "aomi"
            code, out, err = run(["install", "--dir", str(target), "--yes"])
            self.assertEqual(code, 0, err or out)
            self.assertIn("your agent", out)
            self.assertTrue((target / "SKILL.md").is_file())

    def test_custom_directory_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "anywhere" / "aomi"
            code, out, _ = run(["install", "--agent", "cursor", "--dir", str(target), "--yes"])
            self.assertEqual(code, 0, out)
            self.assertTrue((target / "SKILL.md").is_file())


class InstallCommandTest(unittest.TestCase):
    def test_install_without_agent_or_terminal_explains_the_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(pathlib.Path, "cwd", return_value=pathlib.Path(tmp)):
                code, _, err = run(["install"])
        self.assertEqual(code, 2)
        self.assertIn("--agent", err)

    def test_unknown_agent_lists_the_real_ones(self):
        code, _, err = run(["install", "--agent", "vscode"])
        self.assertEqual(code, 2)
        self.assertIn("claude", err)

    def test_interactive_install_asks_then_reports_the_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = pathlib.Path(tmp)
            with mock.patch.object(pathlib.Path, "cwd", return_value=cwd), \
                 mock.patch.object(ui, "is_interactive", return_value=True), \
                 mock.patch.object(ui, "ask", return_value="1"), \
                 mock.patch.object(ui, "confirm", return_value=True):
                code, out, _ = run(["install"])
            self.assertEqual(code, 0, out)
            self.assertIn("Aomi installer", out)
            self.assertIn("Select your agent" if "Select your agent" in out else "select your agent", out)
            self.assertTrue((cwd / ".claude" / "skills" / "aomi" / "SKILL.md").is_file())

    def test_agents_lists_adapters_and_flags_unverified_ones(self):
        code, out, _ = run(["agents"])
        self.assertEqual(code, 0)
        for adapter in adapters.ADAPTERS:
            self.assertIn(adapter.label, out)
        self.assertIn("documented, not run here", out)

    def test_update_finds_what_is_installed_and_refuses_when_there_is_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = pathlib.Path(tmp)
            with mock.patch.object(pathlib.Path, "cwd", return_value=cwd):
                code, _, err = run(["update"])
                self.assertEqual(code, 2)
                self.assertIn("no installed copy", err)
                code, _, _ = run(["install", "--agent", "claude", "--yes"])
                self.assertEqual(code, 0)
                code, out, _ = run(["update"])
                self.assertEqual(code, 0, out)
                self.assertIn("updated", out)

    def test_uninstall_accepts_the_scope_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd, home = pathlib.Path(tmp), pathlib.Path(tmp) / "home"
            home.mkdir()
            with mock.patch.object(pathlib.Path, "cwd", return_value=cwd), \
                 mock.patch.object(pathlib.Path, "home", return_value=home):
                self.assertEqual(run(["install", "--agent", "claude", "--global", "--yes"])[0], 0)
                self.assertTrue((home / ".claude" / "skills" / "aomi" / "SKILL.md").is_file())
                self.assertEqual(run(["uninstall", "--agent", "claude", "--global", "--yes"])[0], 0)
                self.assertFalse((home / ".claude" / "skills" / "aomi").exists())

    def test_uninstall_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            cwd = pathlib.Path(tmp)
            with mock.patch.object(pathlib.Path, "cwd", return_value=cwd):
                run(["install", "--agent", "claude", "--yes"])
                code, out, _ = run(["uninstall", "--yes"])
                self.assertEqual(code, 0, out)
            self.assertFalse((cwd / ".claude" / "skills" / "aomi").exists())


class InitTest(unittest.TestCase):
    def test_default_set_is_unchanged_for_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, _ = run(["init", tmp, "--yes"])
            self.assertEqual(code, 0)
            names = sorted(p.name for p in (pathlib.Path(tmp) / "aomi").iterdir())
        self.assertEqual(names, ["brief.md", "decisions.md", "features.csv",
                                 "handoff.md", "proof.md"])

    def test_sketch_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(["init", tmp, "--depth", "sketch", "--yes"])
            self.assertEqual(code, 0)
            self.assertFalse((pathlib.Path(tmp) / "aomi").exists())
            self.assertIn("nothing", out)

    def test_product_writes_the_full_set_including_the_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(["init", tmp, "--depth", "product", "--yes"])
            names = sorted(p.name for p in (pathlib.Path(tmp) / "aomi").iterdir())
        self.assertIn("map.md", names)
        self.assertEqual(len(names), 6)

    def test_the_brief_carries_the_name_and_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(["init", tmp, "--name", "buku kas", "--depth", "build", "--yes"])
            brief = (pathlib.Path(tmp) / "aomi" / "brief.md").read_text()
        self.assertIn("# Brief: buku kas", brief)
        self.assertIn("**build**", brief)

    def test_a_bad_depth_is_a_usage_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = run(["init", tmp, "--depth", "huge", "--yes"])
        self.assertEqual(code, 2)
        self.assertIn("sketch, build or product", err)

    def test_interactive_init_asks_name_and_depth(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(ui, "is_interactive", return_value=True), \
                 mock.patch.object(ui, "ask", side_effect=["kasir", "3"]), \
                 mock.patch.object(ui, "confirm", return_value=True):
                code, out, _ = run(["init", tmp])
            self.assertEqual(code, 0, out)
            self.assertIn("Aomi project setup", out)
            self.assertTrue((pathlib.Path(tmp) / "aomi" / "map.md").is_file())

    def test_existing_work_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            run(["init", tmp, "--yes"])
            brief = pathlib.Path(tmp) / "aomi" / "brief.md"
            brief.write_text("# mine\n")
            code, out, _ = run(["init", tmp, "--yes"])
            self.assertEqual(brief.read_text(), "# mine\n")
            self.assertIn("kept", out)


class ConfigTest(unittest.TestCase):
    def test_empty_project_shows_nothing_configured_and_still_works(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(["config", "--show", tmp])
            self.assertEqual(code, 0)
            self.assertIn("not present", out)
            code, out, _ = run(["config", "--check", tmp])
            self.assertEqual(code, 0, out)
            self.assertIn("valid setup", out)

    def test_brand_colours_are_written_then_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            configcmd.write_tokens(top, "#F7F4EE", "#1C1A17", "#8C3B52")
            doc = json.loads((top / "aomi" / "tokens.json").read_text())
            self.assertEqual(len(doc["pairs"]), 3)
            code, out, _ = run(["config", "--check", tmp])
            self.assertEqual(code, 0, out)

    def test_a_failing_contrast_pair_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            configcmd.write_tokens(top, "#FFFFFF", "#FDFDFD", "#EEEEEE")
            code, out, _ = run(["config", "--check", tmp])
        self.assertEqual(code, 1)
        self.assertIn("needs", out)

    def test_a_waiver_needs_an_allowed_reason(self):
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            configcmd.add_override(top, "SG01", "brand", "the logo has used it since 2019")
            self.assertEqual(run(["config", "--check", tmp])[0], 0)
            configcmd.add_override(top, "SG05", "because-i-said-so", "")
            code, out, _ = run(["config", "--check", tmp])
        self.assertEqual(code, 1)
        self.assertIn("SG05", out)

    def test_a_feature_row_can_be_scored(self):
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            configcmd.add_feature(top, "core", "Sign up", "must", "yes", "yes")
            code, out, _ = run(["parity", str(top / "aomi" / "features.csv")])
        self.assertEqual(code, 0)
        self.assertIn("100.0", out)

    def test_the_wizard_writes_files_from_answers(self):
        answers = iter(["1", "#F7F4EE", "#1C1A17", "#8C3B52", "6"])
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(ui, "is_interactive", return_value=True), \
                 mock.patch.object(ui, "ask", side_effect=lambda *a, **k: next(answers)):
                code, out, _ = run(["config", tmp])
            self.assertEqual(code, 0, out)
            self.assertTrue((pathlib.Path(tmp) / "aomi" / "tokens.json").is_file())


class AuditUxTest(unittest.TestCase):
    def test_summary_leads_with_counts_and_status(self):
        code, out, _ = run(["audit", str(FIXTURES / "slop")])
        self.assertEqual(code, 1)
        for line in ("files scanned", "issues found", "score", "status", "BLOCKED"):
            self.assertIn(line, out)
        self.assertIn("critical", out)
        self.assertIn("fix:", out)

    def test_the_score_matches_the_json_report(self):
        _, text, _ = run(["audit", str(FIXTURES / "slop")])
        _, data, _ = run(["audit", "--json", str(FIXTURES / "slop")])
        self.assertIn(f"{json.loads(data)['score']}/100", text)

    def test_missing_target_says_where_to_point_it(self):
        code, _, err = run(["audit", str(FIXTURES / "nope")])
        self.assertEqual(code, 2)
        self.assertIn("does not exist", err)

    def test_empty_target_is_not_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = run(["audit", tmp])
        self.assertEqual(code, 0)
        self.assertIn("Nothing to audit", out)


class PayloadTest(unittest.TestCase):
    def test_the_payload_is_the_skill_not_the_repository(self):
        rel = {name for name, _ in paths.payload_files()}
        for required in ("SKILL.md", "core/workflow.md", "design/slop-gate.md",
                         "templates/brief.md", "docs/provenance.md", "LICENSE"):
            self.assertIn(required, rel)
        self.assertFalse([r for r in rel if r.startswith("tests/")])
        self.assertFalse([r for r in rel if r.split("/")[0] in {"aomi", ".git"}])
        for development_file in ("scripts/aomi.py", "scripts/build_assets.py",
                                 "pyproject.toml", "setup.py", "MANIFEST.in"):
            self.assertNotIn(development_file, rel, f"{development_file} is a development file")
        # the one script that ships: the wrapper a script runner calls
        self.assertIn("scripts/run.sh", rel)

    def test_every_relative_link_in_the_payload_resolves_inside_the_payload(self):
        """The install copies only payload files, so a link outside it would break."""
        rel = {name for name, _ in paths.payload_files()}
        broken = []
        root = paths.skill_root()
        for name, source in paths.payload_files():
            if not name.endswith(".md"):
                continue
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source.read_text(errors="ignore")):
                if target.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                clean = target.split("#")[0].strip()
                if not clean:
                    continue
                resolved = (source.parent / clean).resolve()
                try:
                    inside = resolved.relative_to(root).as_posix()
                except ValueError:
                    broken.append(f"{name} -> {clean} (outside the skill)")
                    continue
                is_file = inside in rel
                is_folder = any(entry.startswith(inside.rstrip("/") + "/") for entry in rel)
                if not (is_file or is_folder):
                    broken.append(f"{name} -> {clean}")
        self.assertEqual(broken, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
