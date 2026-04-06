"""Unit tests for manim/worker.py

Tests cover all pure-logic helpers (text cleaning, code sanitization,
markdown stripping, fallback scene generation) and the Gemini-calling /
job-processing functions via mocks.

Run:  pytest manim/test_worker.py -v
"""

import json
import os
import shutil
import sys
import tempfile
from unittest import mock

import pytest

# Ensure the manim directory is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from worker import (
    _clean_response_text,
    _fallback_scene,
    _fix_common_manim_bugs,
    _sanitize_generated_code,
    _strip_markdown_fences,
    _strip_mathtex_from_code,
    _wrap_text,
    generate_manim_code,
    process_job,
)


# ---------------------------------------------------------------------------
# _clean_response_text
# ---------------------------------------------------------------------------
class TestCleanResponseText:
    """Tests for stripping markdown from Gemini responses."""

    def test_removes_bold(self):
        assert _clean_response_text("**bold**") == "bold"

    def test_removes_italic_asterisk(self):
        assert _clean_response_text("*italic*") == "italic"

    def test_removes_bold_underscore(self):
        assert _clean_response_text("__bold__") == "bold"

    def test_removes_italic_underscore(self):
        assert _clean_response_text("_italic_") == "italic"

    def test_removes_headers(self):
        md = "## Introduction\nSome text\n### Details\nMore text"
        result = _clean_response_text(md)
        assert "##" not in result
        assert "Introduction" in result
        assert "Details" in result

    def test_removes_bullet_points(self):
        md = "- Item one\n* Item two\n• Item three"
        result = _clean_response_text(md)
        assert result == "Item one\nItem two\nItem three"

    def test_removes_numbered_lists(self):
        md = "1. First\n2. Second"
        result = _clean_response_text(md)
        assert "1." not in result
        assert "First" in result

    def test_removes_markdown_links(self):
        md = "Click [here](https://example.com) for details"
        result = _clean_response_text(md)
        assert result == "Click here for details"

    def test_collapses_blank_lines(self):
        md = "Line one\n\n\n\n\nLine two"
        result = _clean_response_text(md)
        assert "\n\n\n" not in result
        assert "Line one" in result and "Line two" in result

    def test_strips_whitespace(self):
        assert _clean_response_text("  hello  ") == "hello"

    def test_empty_string(self):
        assert _clean_response_text("") == ""

    def test_plain_text_unchanged(self):
        text = "Newton's second law states F = ma."
        assert _clean_response_text(text) == text


# ---------------------------------------------------------------------------
# _sanitize_generated_code
# ---------------------------------------------------------------------------
class TestSanitizeGeneratedCode:
    """Tests for cleaning problem patterns from Gemini-generated Manim code."""

    def test_removes_text_command(self):
        code = r'MathTex("E = mc^2 \text{ Joules}")'
        result = _sanitize_generated_code(code)
        assert r"\text" not in result
        assert "MathTex" in result

    def test_removes_textbf(self):
        code = r'MathTex("\textbf{Force}")'
        result = _sanitize_generated_code(code)
        assert r"\textbf" not in result

    def test_removes_textit(self):
        code = r'MathTex("\textit{mass}")'
        result = _sanitize_generated_code(code)
        assert r"\textit" not in result

    def test_removes_mathrm(self):
        code = r'MathTex("\mathrm{kg}")'
        result = _sanitize_generated_code(code)
        assert r"\mathrm" not in result

    def test_removes_mbox_and_hbox(self):
        code = r'MathTex("\mbox{text} \hbox{more}")'
        result = _sanitize_generated_code(code)
        assert r"\mbox" not in result
        assert r"\hbox" not in result

    def test_removes_control_tokens(self):
        code = 'from manim import *<ctrl63>\nclass Scene(Scene): pass'
        result = _sanitize_generated_code(code)
        assert "<ctrl" not in result
        assert "from manim import *" in result

    def test_keeps_valid_code(self):
        code = 'from manim import *\n\nclass GeneratedScene(Scene):\n    pass'
        assert _sanitize_generated_code(code) == code


# ---------------------------------------------------------------------------
# _fix_common_manim_bugs
# ---------------------------------------------------------------------------
class TestFixCommonManimBugs:
    """Tests for fixing typos and invalid patterns in generated Manim code."""

    def test_fixes_double_frame_width(self):
        code = "config.frame_frame_width"
        assert "frame_width" in _fix_common_manim_bugs(code)
        assert "frame_frame_width" not in _fix_common_manim_bugs(code)

    def test_removes_width_kwarg_from_text(self):
        code = 'Text("hello", font_size=28, width=config.frame_width - 2)'
        result = _fix_common_manim_bugs(code)
        assert "width=" not in result
        assert 'Text("hello", font_size=28)' == result

    def test_replaces_width_assignment(self):
        code = "title.width = 5"
        result = _fix_common_manim_bugs(code)
        assert ".scale_to_fit_width(" in result

    def test_leaves_clean_code_alone(self):
        code = 'Text("hello", font_size=28, color=WHITE)'
        assert _fix_common_manim_bugs(code) == code


# ---------------------------------------------------------------------------
# _strip_mathtex_from_code
# ---------------------------------------------------------------------------
class TestStripMathTexFromCode:
    """Tests for the MathTex → Text last-resort converter."""

    def test_converts_mathtex_to_text(self):
        code = 'eq = MathTex("E = mc^2")'
        result = _strip_mathtex_from_code(code)
        assert "Text(" in result
        assert "MathTex(" not in result

    def test_replaces_latex_symbols(self):
        code = 'eq = MathTex("\\frac{a}{b} \\times c")'
        result = _strip_mathtex_from_code(code)
        assert "×" in result
        assert "\\times" not in result

    def test_replaces_delta_and_sqrt(self):
        code = 'eq = MathTex("\\Delta x = \\sqrt{y}")'
        result = _strip_mathtex_from_code(code)
        assert "Δ" in result
        assert "√" in result

    def test_replaces_sum_and_int(self):
        code = 'eq = MathTex("\\sum \\int f(x)")'
        result = _strip_mathtex_from_code(code)
        assert "Σ" in result
        assert "∫" in result

    def test_no_mathtex_unchanged(self):
        code = 'title = Text("Hello World")'
        assert _strip_mathtex_from_code(code) == code


# ---------------------------------------------------------------------------
# _strip_markdown_fences
# ---------------------------------------------------------------------------
class TestStripMarkdownFences:
    """Tests for removing code fences and trailing explanations."""

    def test_removes_python_fences(self):
        code = "```python\nfrom manim import *\nclass S(Scene): pass\n```"
        result = _strip_markdown_fences(code)
        assert "```" not in result
        assert "from manim import *" in result

    def test_removes_plain_fences(self):
        code = "```\ncode here\n```"
        result = _strip_markdown_fences(code)
        assert "```" not in result
        assert "code here" in result

    def test_removes_instruction_tags(self):
        code = "from manim import *\n[instruction] Render this scene"
        result = _strip_markdown_fences(code)
        assert "[instruction]" not in result.lower()
        assert "from manim import *" in result

    def test_removes_trailing_explanation(self):
        code = "from manim import *\nclass S(Scene): pass\nThis code creates a scene."
        result = _strip_markdown_fences(code)
        assert "This code" not in result

    def test_removes_note_explanation(self):
        code = "from manim import *\nclass S(Scene): pass\nNote: run with manim"
        result = _strip_markdown_fences(code)
        assert "Note:" not in result

    def test_clean_code_unchanged(self):
        code = "from manim import *\n\nclass GeneratedScene(Scene):\n    pass"
        assert _strip_markdown_fences(code) == code

    def test_strips_whitespace(self):
        code = "  \n from manim import *\n  "
        result = _strip_markdown_fences(code)
        assert result == "from manim import *"


# ---------------------------------------------------------------------------
# _fallback_scene
# ---------------------------------------------------------------------------
class TestFallbackScene:
    """Tests for the fallback scene generator."""

    def test_contains_scene_boilerplate(self):
        code = _fallback_scene("Gravity", "Objects fall due to gravity.")
        assert "from manim import *" in code
        assert "class GeneratedScene(Scene):" in code
        assert "def construct(self):" in code
        assert '#0a1224' in code

    def test_contains_topic_as_title(self):
        code = _fallback_scene("Newton's Laws", "Force equals mass times acceleration.")
        assert "Newton" in code

    def test_escapes_quotes_in_topic(self):
        code = _fallback_scene('He said "hello"', "Some text.")
        # Double quotes should be replaced with single quotes
        assert '"hello"' not in code or "'" in code

    def test_creates_multi_line_slides(self):
        long_text = "word " * 200  # ~1000 chars
        code = _fallback_scene("Test", long_text)
        # Should use line_X_Y naming and VGroup
        assert "line_0_0" in code
        assert "VGroup" in code
        assert "slide_0" in code

    def test_max_six_slides(self):
        very_long = "word " * 2000
        code = _fallback_scene("Test", very_long)
        assert "slide_5" in code     # 6th slide (0-indexed)
        assert "slide_6" not in code  # no 7th

    def test_short_text_single_slide(self):
        code = _fallback_scene("Test", "Short text here.")
        assert "slide_0" in code
        assert "slide_1" not in code

    def test_has_step_indicator(self):
        code = _fallback_scene("Test", "Some text to display.")
        assert "step_0" in code
        assert "to_corner" in code

    def test_empty_response_text(self):
        code = _fallback_scene("Topic", "")
        # Should still produce valid scene structure
        assert "from manim import *" in code
        assert "GeneratedScene" in code

    def test_uses_scale_to_fit_width(self):
        code = _fallback_scene("Test", "Some content for the video.")
        assert "scale_to_fit_width" in code
        assert "width =" not in code  # no direct width assignment


# ---------------------------------------------------------------------------
# generate_manim_code (mocked Gemini)
# ---------------------------------------------------------------------------
class TestGenerateManimCode:
    """Tests for generate_manim_code with mocked Gemini API."""

    def test_no_api_key_returns_fallback(self):
        with mock.patch("worker.GEMINI_API_KEY", ""):
            code = generate_manim_code("Topic", "Some text")
            # Should be a fallback scene
            assert "GeneratedScene" in code
            assert "from manim import *" in code

    def test_successful_gemini_response(self):
        valid_code = (
            'from manim import *\n\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self):\n'
            '        self.camera.background_color = "#0a1224"\n'
        )
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = mock.Mock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": valid_code}}]
        }

        with mock.patch("worker.GEMINI_API_KEY", "fake-key"), \
             mock.patch("worker.requests.post", return_value=mock_resp):
            code = generate_manim_code("Physics", "F = ma")
            assert "GeneratedScene" in code
            assert "from manim" in code

    def test_invalid_gemini_response_returns_fallback(self):
        """If Gemini returns code without GeneratedScene, use fallback."""
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "print('hello')"}}]
        }

        with mock.patch("worker.GEMINI_API_KEY", "fake-key"), \
             mock.patch("worker.requests.post", return_value=mock_resp):
            code = generate_manim_code("Math", "2+2=4")
            assert "GeneratedScene" in code  # fallback always has this

    def test_gemini_exception_returns_fallback(self):
        with mock.patch("worker.GEMINI_API_KEY", "fake-key"), \
             mock.patch("worker.requests.post", side_effect=Exception("timeout")):
            code = generate_manim_code("Topic", "Text")
            assert "GeneratedScene" in code

    def test_gemini_503_retries(self):
        """503 should trigger retry logic."""
        error_resp = mock.Mock()
        error_resp.status_code = 503
        http_error = __import__("requests").exceptions.HTTPError(response=error_resp)

        ok_code = (
            'from manim import *\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self): pass\n'
        )
        ok_resp = mock.Mock()
        ok_resp.raise_for_status = mock.Mock()
        ok_resp.json.return_value = {
            "choices": [{"message": {"content": ok_code}}]
        }

        with mock.patch("worker.GEMINI_API_KEY", "fake-key"), \
             mock.patch("worker.requests.post", side_effect=[http_error, ok_resp]), \
             mock.patch("worker.time.sleep"):  # skip delay
            code = generate_manim_code("Topic", "Text")
            assert "GeneratedScene" in code

    def test_strips_fences_from_response(self):
        fenced = "```python\nfrom manim import *\nclass GeneratedScene(Scene):\n    pass\n```"
        mock_resp = mock.Mock()
        mock_resp.raise_for_status = mock.Mock()
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": fenced}}]
        }

        with mock.patch("worker.GEMINI_API_KEY", "fake-key"), \
             mock.patch("worker.requests.post", return_value=mock_resp):
            code = generate_manim_code("T", "text")
            assert "```" not in code


# ---------------------------------------------------------------------------
# process_job (mocked filesystem + subprocess)
# ---------------------------------------------------------------------------
class TestProcessJob:
    """Tests for the job processing pipeline with mocked I/O."""

    @pytest.fixture(autouse=True)
    def setup_dirs(self, tmp_path):
        """Set up temp directories mimicking the worker's folder layout."""
        self.incoming = tmp_path / "jobs" / "incoming"
        self.done = tmp_path / "jobs" / "done"
        self.failed = tmp_path / "jobs" / "failed"
        self.rendered = tmp_path / "media" / "rendered"
        self.scenes = tmp_path / "generated_scenes"
        self.video_out = tmp_path / "media" / "videos"

        for d in [self.incoming, self.done, self.failed, self.rendered, self.scenes, self.video_out]:
            d.mkdir(parents=True, exist_ok=True)

        # Patch module-level directory constants
        self._patches = [
            mock.patch("worker.INCOMING", str(self.incoming)),
            mock.patch("worker.DONE", str(self.done)),
            mock.patch("worker.FAILED", str(self.failed)),
            mock.patch("worker.RENDERED", str(self.rendered)),
            mock.patch("worker.SCENES_DIR", str(self.scenes)),
            mock.patch("worker.MANIM_OUTPUT_DIR", str(self.video_out)),
        ]
        for p in self._patches:
            p.start()

        yield

        for p in self._patches:
            p.stop()

    def _create_job(self, lesson_id, topic="Test", response_text="Hello world"):
        """Helper: write a job JSON into incoming/."""
        job = {"topic": topic, "response_text": response_text}
        job_file = f"{lesson_id}.json"
        path = self.incoming / job_file
        path.write_text(json.dumps(job))
        return job_file

    def test_skips_already_rendered(self):
        """If video already exists, job moves to done without rendering."""
        job_file = self._create_job("cached-id")
        # Pre-place the video
        (self.rendered / "cached-id.mp4").write_bytes(b"\x00" * 100)

        process_job(job_file)

        assert (self.done / job_file).exists()
        assert not (self.incoming / job_file).exists()

    def test_successful_render(self):
        """Happy path: Gemini generates code, manim renders, video is copied."""
        job_file = self._create_job("new-job")

        valid_code = (
            'from manim import *\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self): pass\n'
        )

        # Mock Gemini to return valid code
        with mock.patch("worker.generate_manim_code", return_value=valid_code):
            # Mock subprocess: create the expected output file
            def fake_run(cmd, **kwargs):
                # Simulate manim creating the output video
                scene_name = "new-job"
                out_dir = self.video_out / scene_name / "480p15"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "GeneratedScene.mp4").write_bytes(b"\x00" * 50)
                return mock.Mock(stdout="", stderr="", returncode=0)

            with mock.patch("worker.subprocess.run", side_effect=fake_run):
                process_job(job_file)

        assert (self.rendered / "new-job.mp4").exists()
        assert (self.done / job_file).exists()

    def test_render_uses_os_walk_fallback(self):
        """If video isn't in the expected dir, os.walk should find it."""
        job_file = self._create_job("walk-job")

        valid_code = (
            'from manim import *\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self): pass\n'
        )

        with mock.patch("worker.generate_manim_code", return_value=valid_code):
            def fake_run(cmd, **kwargs):
                # Put video in an unexpected subdirectory
                weird_dir = self.video_out / "walk-job" / "720p30"
                weird_dir.mkdir(parents=True, exist_ok=True)
                (weird_dir / "GeneratedScene.mp4").write_bytes(b"\x00" * 50)
                return mock.Mock(stdout="done", stderr="", returncode=0)

            with mock.patch("worker.subprocess.run", side_effect=fake_run):
                process_job(job_file)

        assert (self.rendered / "walk-job.mp4").exists()

    def test_empty_response_text_fails(self):
        """Job with empty response_text should fail gracefully."""
        job = {"topic": "Test", "response_text": ""}
        job_file = "empty-resp.json"
        (self.incoming / job_file).write_text(json.dumps(job))

        process_job(job_file)

        assert (self.failed / job_file).exists()

    def test_subprocess_failure_triggers_fallback(self):
        """When manim crashes, fallback scene should be attempted."""
        job_file = self._create_job("crash-job", response_text="Some content here")

        valid_code = (
            'from manim import *\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self): pass\n'
        )

        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call fails (primary render)
                raise __import__("subprocess").CalledProcessError(
                    1, cmd, output="", stderr="SomeError: something broke"
                )
            else:
                # Fallback render succeeds
                out_dir = self.video_out / "crash-job_fallback" / "1080p30"
                out_dir.mkdir(parents=True, exist_ok=True)
                (out_dir / "GeneratedScene.mp4").write_bytes(b"\x00" * 50)
                return mock.Mock(stdout="", stderr="", returncode=0)

        with mock.patch("worker.generate_manim_code", return_value=valid_code), \
             mock.patch("worker.subprocess.run", side_effect=fake_run):
            process_job(job_file)

        assert (self.rendered / "crash-job.mp4").exists()

    def test_latex_error_strips_mathtex_and_retries(self):
        """LaTeX errors should trigger MathTex stripping retry."""
        job_file = self._create_job("latex-err", response_text="Some formula")

        code_with_mathtex = (
            'from manim import *\n'
            'class GeneratedScene(Scene):\n'
            '    def construct(self):\n'
            '        eq = MathTex("E = mc^2")\n'
        )

        call_count = 0

        def fake_run(cmd, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise __import__("subprocess").CalledProcessError(
                    1, cmd, output="", stderr="! LaTeX Error: something"
                )
            else:
                # Retry succeeds — place video
                for root_dir in [self.video_out]:
                    out = root_dir / "latex-err_notex" / "1080p30"
                    out.mkdir(parents=True, exist_ok=True)
                    (out / "GeneratedScene.mp4").write_bytes(b"\x00" * 50)
                return mock.Mock(stdout="", stderr="", returncode=0)

        with mock.patch("worker.generate_manim_code", return_value=code_with_mathtex), \
             mock.patch("worker.subprocess.run", side_effect=fake_run):
            process_job(job_file)

        assert (self.rendered / "latex-err.mp4").exists()
        assert call_count == 2  # original + MathTex-stripped retry


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
