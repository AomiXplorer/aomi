"""Tests for install.py: the route that does not need pip.

These run the real code path against a throwaway HOME, then run the launcher the
installer wrote, because a launcher that is not executable or cannot import the
package is the failure that matters.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from aomi import bootstrap  # noqa: E402


def run(argv: list[str], cwd: pathlib.Path, home: pathlib.Path) -> subprocess.CompletedProcess:
    env = {"PATH": f"{home / '.local' / 'bin'}:/usr/local/bin:/usr/bin:/bin",
           "HOME": str(home), "LANG": "C.UTF-8"}
    return subprocess.run([sys.executable, str(ROOT / "install.py"), *argv],
                          cwd=str(cwd), env=env, capture_output=True, text=True)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        self.app = self.home / ".local" / "share" / "aomi"
        self.launcher = self.home / ".local" / "bin" / "aomi"

    def tearDown(self):
        self.tmp.cleanup()

    # ---------------------------------------------------------------- command

    def test_yes_installs_the_command_and_it_runs(self):
        result = run(["--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue(self.launcher.is_file())
        self.assertTrue(os.access(self.launcher, os.X_OK))
        version = subprocess.run([str(self.launcher), "--version"], capture_output=True, text=True)
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertIn("aomi 1.1.0", version.stdout)

    def test_no_pip_no_venv_no_root_needed(self):
        result = run(["--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0)
        launcher_text = self.launcher.read_text()
        self.assertNotIn("-m pip", launcher_text)
        self.assertNotIn("sudo", launcher_text)
        self.assertIn(str(self.app), launcher_text)

    def test_the_payload_lands_where_the_command_expects_it(self):
        run(["--yes"], self.project, self.home)
        self.assertTrue((self.app / "SKILL.md").is_file())
        self.assertTrue((self.app / "aomi" / "cli.py").is_file())
        self.assertTrue((self.app / "core" / "workflow.md").is_file())
        self.assertTrue(os.access(self.app / "scripts" / "run.sh", os.X_OK))

    def test_no_repository_files_travel_with_the_command(self):
        run(["--yes"], self.project, self.home)
        for name in ("tests", ".git", ".github", "pyproject.toml", "setup.py", "install.py"):
            self.assertFalse((self.app / name).exists(), f"{name} should not be installed")

    def test_second_run_updates_in_place(self):
        run(["--yes"], self.project, self.home)
        first = sorted(p.relative_to(self.app).as_posix() for p in self.app.rglob("*") if p.is_file())
        result = run(["--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0)
        second = sorted(p.relative_to(self.app).as_posix() for p in self.app.rglob("*") if p.is_file())
        self.assertEqual(first, second)
        self.assertFalse((self.app / "aomi" / "aomi").exists())

    def test_a_stale_bundled_copy_is_removed(self):
        run(["--yes"], self.project, self.home)
        bundled = self.app / "aomi" / "skilldata"
        bundled.mkdir()
        (bundled / "SKILL.md").write_text("old\n")
        run(["--yes"], self.project, self.home)
        self.assertFalse(bundled.exists(), "a stale bundle would shadow the real payload")

    def test_python_version_note_is_honest(self):
        # the launcher must call the interpreter that installed it, so a second
        # interpreter on PATH cannot silently change what `aomi` runs
        run(["--yes"], self.project, self.home)
        self.assertIn(sys.executable, self.launcher.read_text())

    def test_uninstall_removes_both_halves(self):
        run(["--yes"], self.project, self.home)
        result = run(["--uninstall", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.launcher.exists())
        self.assertFalse(self.app.exists())

    def test_uninstall_says_so_when_nothing_is_there(self):
        result = run(["--uninstall", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0)
        self.assertIn("nothing installed", result.stdout)

    def test_dry_run_writes_nothing(self):
        result = run(["--command", "--dry-run"], self.project, self.home)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(self.launcher.exists())
        self.assertFalse(self.app.exists())

    def test_termux_uses_the_prefix_that_is_already_on_path(self):
        env = {"HOME": "/data/data/com.termux/files/home", "TERMUX_VERSION": "0.118",
               "PREFIX": "/data/data/com.termux/files/usr"}
        self.assertTrue(bootstrap.is_termux(env))
        self.assertEqual(bootstrap.default_bin_dir(env),
                         pathlib.Path("/data/data/com.termux/files/usr/bin"))
        self.assertEqual(bootstrap.default_bin_dir({"HOME": "/home/ana"}),
                         pathlib.Path("/home/ana/.local/bin"))

    def test_launcher_does_not_need_bin_sh(self):
        # Termux has no /bin, and termux-exec is not guaranteed, so a #!/bin/sh
        # launcher is the one thing that breaks there
        run(["--yes"], self.project, self.home)
        first = self.launcher.read_text().splitlines()[0]
        self.assertTrue(first.startswith("#!"))
        self.assertNotIn("/bin/sh", first)
        self.assertIn("python", first)

    def test_path_advice_names_the_right_file_for_the_shell(self):
        line, rc = bootstrap.path_advice(self.launcher.parent, {"SHELL": "/bin/zsh"})
        self.assertIn(".zshrc", rc)
        self.assertIn(str(self.launcher.parent), line)
        line, rc = bootstrap.path_advice(self.launcher.parent, {"SHELL": "/usr/bin/fish"})
        self.assertIn("fish_add_path", line)
        line, rc = bootstrap.path_advice(self.launcher.parent, {"SHELL": "/bin/sh"})
        self.assertIn(".profile", rc)

    def test_on_path_is_decided_from_the_environment_we_are_given(self):
        bin_dir = self.home / ".local" / "bin"
        self.assertFalse(bootstrap.on_path(bin_dir, {"PATH": "/usr/bin:/bin"}))
        self.assertTrue(bootstrap.on_path(bin_dir, {"PATH": f"/usr/bin:{bin_dir}"}))

    # ------------------------------------------------------------------ skill

    def test_skill_only_installs_into_an_agent_folder(self):
        result = run(["--skill", "--agent", "cursor", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        target = self.project / ".cursor" / "skills" / "aomi"
        self.assertTrue((target / "SKILL.md").is_file())
        self.assertFalse((target / "tests").exists())
        self.assertFalse(self.launcher.exists(), "skill-only should not touch the command")

    def test_both_halves_in_one_run(self):
        result = run(["--command", "--skill", "--agent", "cursor", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue(self.launcher.is_file())
        self.assertTrue((self.project / ".cursor" / "skills" / "aomi" / "SKILL.md").is_file())

    def test_unknown_agent_is_refused_with_the_list(self):
        result = run(["--skill", "--agent", "nope", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("claude", result.stderr)

    def test_skill_without_an_agent_and_without_a_terminal_says_what_to_pass(self):
        result = run(["--skill", "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 2)
        self.assertIn("--agent", result.stderr)

    def test_custom_directory_needs_no_agent_name(self):
        target = self.root / "somewhere" / "aomi"
        result = run(["--skill", "--dir", str(target), "--yes"], self.project, self.home)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertTrue((target / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
