import glob
import os
import json
import re
import time
import shutil
import subprocess
import requests
import concurrent.futures
from dotenv import load_dotenv

BASE = os.path.dirname(os.path.abspath(__file__))
# Load .env from project root
load_dotenv(dotenv_path=os.path.join(BASE, "..", ".env"), override=True)

# Central user data root location (e.g. /home/yash/SQ/user_data)
USER_DATA_ROOT = os.path.abspath(os.path.join(BASE, "..", "user_data"))
os.makedirs(USER_DATA_ROOT, exist_ok=True)

# The manim output location (fixed by manim's naming convention)
MANIM_OUTPUT_DIR = os.path.join(BASE, "media", "videos")


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")
    
GEMINI_MODEL = "gemini-2.0-flash-lite"
GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
)

# The manim output location (fixed by manim's naming convention)
MANIM_OUTPUT_DIR = os.path.join(BASE, "media", "videos")

MANIM_CODE_PROMPT = r"""
You are a Manim Community Edition (v0.19) code generator for educational animations.

Convert the following educational content into a **single, self-contained Manim scene**.

The output frame is 14.22 × 8 Manim units (config.frame_width × config.frame_height).
Keep ALL content within a safe zone of 1 unit from every edge.

STRICT RULES — follow every one:

1. Start with `from manim import *`
2. Define exactly ONE class called `GeneratedScene(Scene):`
3. Set background: `self.camera.background_color = "#0a1224"` in `construct()`
4. Use `Text(...)` for explanations (**never** use `Tex` for plain text).
   - **CRITICAL**: NEVER use `width=` kwarg in Text() — it does not exist.
     Instead call `.scale_to_fit_width(config.frame_width - 2)` AFTER creating the Text object:
       `t = Text("Hello", font_size=28); t.scale_to_fit_width(config.frame_width - 2)`
   - Keep each `Text()` to max ~60 characters. For longer content, split into MULTIPLE
     `Text()` objects grouped with `VGroup(...).arrange(DOWN, buff=0.3)`.
   - Use `font_size=24` for body text, `font_size=36` for titles.
5. Use `MathTex(...)` for LaTeX equations/formulas.
   - **CRITICAL LaTeX rules for MathTex:**
     - NEVER use `\text{{}}` — it causes compilation errors. Use plain `Text()` objects beside the equation instead.
     - NEVER mix units or words inside MathTex. Keep MathTex ONLY for pure math: variables, operators, numbers.
     - For units like "kg", "m/s", "MeV", put them in a separate `Text()` positioned next to the equation.
     - Use ONLY basic LaTeX: `^`, `_`, `\frac{{}}{{}}`, `\sqrt{{}}`, `\times`, `\cdot`, `\Delta`, `\sum`, `\int`, `\vec{{}}`, `\hat{{}}`.
     - NEVER use `\textbf`, `\textit`, `\mathrm`, `\mbox`, `\hbox` inside MathTex.
     - For long equations, use `font_size=32` and break across lines using `\\\\` inside an `aligned` environment.
     - Always test: if the LaTeX string has English words in it, those words should be in a separate `Text()`, NOT in `MathTex()`.
6. Use animations: `Write`, `FadeIn`, `FadeOut`, `Create`, `Transform`, `ReplacementTransform`
7. Add `self.wait(1)` to `self.wait(2)` between sections so the viewer can read.
8. Keep the total animation under 60 seconds (about 15-20 animation steps). Be concise — fewer steps renders faster.
9. Use colors: `BLUE_C`, `YELLOW_C`, `GREEN_C`, `RED_C`, `WHITE`, `GREY_A` for variety.
10. Position elements carefully — use `.to_edge()`, `.shift()`, `.next_to()` to avoid overlaps.
    - Keep a margin of at least 1 unit from all screen edges.
    - Use `VGroup(...).arrange(DOWN, buff=0.3)` to stack text blocks vertically.
    - Center content vertically: `group.move_to(ORIGIN)` or `group.next_to(title, DOWN, buff=0.6)`
11. Clear the screen with `self.play(FadeOut(*self.mobjects))` between major sections.
12. DO NOT use any external files, images, SVGs, or custom fonts.
13. DO NOT use `Tex()` — only `Text()` and `MathTex()`.
14. Output ONLY valid Python code. No markdown fences, no comments outside the code, no explanations.
15. Structure each section as: Title → Key points (2-3 short lines in a VGroup) → Equation (if any) → Clear screen → Next section.
16. NEVER put a long paragraph in a single `Text()`. Break content into bite-sized pieces across multiple frames.
17. **CRITICAL**: Do NOT add ANY explanatory text, comments, or [instruction] tags after the code ends. Output ONLY the Python code itself.
18. CRITICAL STRING RULES:
    - NEVER include line breaks inside Text("...")
    - NEVER include unescaped apostrophes like: A's → use: As or A\'s
    - Each Text() must be a SINGLE LINE string
## Topic: {topic}

## Content to animate:
{response_text}

REMEMBER: Output ONLY the Python code. No explanations before or after. No [instruction] tags. Just pure Python code.
"""


def _clean_response_text(response_text):
    """Strip markdown formatting and extract only the core educational content
    from the last Gemini response so only clean, plain text goes to the
    Manim code generator."""
    text = response_text.strip()

    # Remove markdown bold/italic markers
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)

    # Remove markdown headers (## Header -> Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # Remove bullet point markers
    text = re.sub(r'^\s*[-•*]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)

    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Collapse multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def _sanitize_generated_code(code):
    """Fix common problems in Gemini-generated Manim code."""
    # Strip non-printable / control characters (keep newlines, tabs, spaces)
    code = re.sub(r'[^\x09\x0a\x0d\x20-\x7e\x80-\uffff]', '', code)
    # Remove HTML-like control tokens Gemini sometimes emits (e.g. <ctrl63>)
    code = re.sub(r'<ctrl\d+>', '', code)

    # Replace \text{...} inside MathTex strings with just the content stripped
    # e.g. MathTex("E = mc^2 \\text{ Joules}") -> MathTex("E = mc^2")
    # We remove \text{...} blocks since they break dvi compilation
    code = re.sub(r'\\text\s*\{[^}]*\}', '', code)
    code = re.sub(r'\\textbf\s*\{[^}]*\}', '', code)
    code = re.sub(r'\\textit\s*\{[^}]*\}', '', code)
    code = re.sub(r'\\mathrm\s*\{[^}]*\}', '', code)
    code = re.sub(r'\\mbox\s*\{[^}]*\}', '', code)
    code = re.sub(r'\\hbox\s*\{[^}]*\}', '', code)
    # Force scale_to_fit_width after every Text()
    # Fix unterminated/multiline strings inside Text(...)
    def fix_text_strings(match):
        content = match.group(1)

        # Replace newlines inside string with space
        content = content.replace("\n", " ")

        # Escape single quotes properly
        content = content.replace("'", "\\'")

        return f'Text("{content}")'

    code = re.sub(
        r'Text\("([^"]*?)"\)',
        fix_text_strings,
        code,
        flags=re.DOTALL
    )
    return code
def _fix_common_manim_bugs(code: str) -> str:
    # Fix wrong config attribute
    code = code.replace("frame_frame_width", "frame_width")

    # Remove invalid width=... inside Text()
    code = re.sub(
        r'Text\(([^)]*?),\s*width\s*=\s*[^)]+\)',
        r'Text(\1)',
        code
    )

    # Fix fallback-style width usage
    code = code.replace(".width =", ".scale_to_fit_width(")
    
    return code


def _strip_mathtex_from_code(code):
    """Replace all MathTex(...) calls with Text(...) equivalents.
    Used as a last-resort fix when LaTeX compilation fails."""
    # Match MathTex("...", ...) and convert to Text("...", ...)
    # Replace MathTex with Text and remove LaTeX-specific backslash commands
    def _mathtex_to_text(match):
        full = match.group(0)
        # Replace MathTex -> Text
        result = full.replace('MathTex(', 'Text(', 1)
        return result

    code = re.sub(r'MathTex\([^)]+\)', _mathtex_to_text, code)
    # Clean up LaTeX syntax that would look ugly in plain Text
    # Do this line by line only inside Text() calls that were converted
    code = code.replace('\\frac', '').replace('\\times', '×')
    code = code.replace('\\cdot', '·').replace('\\Delta', 'Δ')
    code = code.replace('\\sum', 'Σ').replace('\\int', '∫')
    code = code.replace('\\vec', '').replace('\\hat', '')
    code = code.replace('\\sqrt', '√')
    return code

def _inject_layout_guard(code: str) -> str:
    guard = """

def enforce_safe_layout(mobj):
    if hasattr(mobj, "width") and mobj.width > config.frame_width - 2:
        mobj.scale_to_fit_width(config.frame_width - 2)
    if hasattr(mobj, "height") and mobj.height > config.frame_height - 2:
        mobj.scale_to_fit_height(config.frame_height - 2)
    mobj.move_to(ORIGIN)
    return mobj
"""
    return code + guard

def generate_manim_code(topic, response_text):
    """Call Gemini to generate manim code from the AI response.
    Only the last Gemini response (cleaned of markdown) is sent."""
    if not GEMINI_API_KEY:
        print("WARNING: No GEMINI_API_KEY set, using fallback scene")
        return _fallback_scene(topic, response_text)

    # Clean the raw Gemini response: strip markdown, keep only plain text
    cleaned = _clean_response_text(response_text)
    cleaned = "\n".join(_wrap_text(cleaned, 55))
    prompt = MANIM_CODE_PROMPT.format(
        topic=topic,
        response_text=cleaned[:3000],  # Keep short for faster code-gen
    )

    # Retry logic for handling temporary API failures
    max_retries = 2
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                GEMINI_URL,
                headers={
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": GEMINI_MODEL,
                    "reasoning_effort": "low",
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            code = data["choices"][0]["message"]["content"]

            # Strip markdown fences if Gemini wraps the code
            code = _strip_markdown_fences(code)

            # Basic validation
            if "GeneratedScene" not in code or "from manim" not in code:
                print("WARNING: Generated code looks invalid, using fallback")
                return _fallback_scene(topic, response_text)

            # Sanitize problematic LaTeX commands
            code = _sanitize_generated_code(code)
            code = _fix_common_manim_bugs(code)
            code = _inject_layout_guard(code)
            return code

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 503 and attempt < max_retries - 1:
                # Service unavailable - retry with exponential backoff
                wait_time = retry_delay * (2 ** attempt)
                print(f"Gemini API unavailable (503), retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                print(f"Gemini code generation failed: {e}")
                return _fallback_scene(topic, response_text)
        except Exception as e:
            print(f"Gemini code generation failed: {e}")
            return _fallback_scene(topic, response_text)


def _strip_markdown_fences(code):
    """Remove ```python ... ``` wrappers, instruction tags, and explanatory text."""
    code = code.strip()
    
    # Remove [instruction] tags and everything after them
    # These are sometimes added by Gemini as explanatory comments
    if '[instruction]' in code.lower():
        # Find the first occurrence (case-insensitive)
        match = re.search(r'\[instruction\]', code, re.IGNORECASE)
        if match:
            code = code[:match.start()].rstrip()
    
    # Also remove common trailing explanation patterns
    # e.g., "This code does...", "The above code...", "Note: ..."
    code = re.sub(
        r'\n\s*(This code|The above code|The provided code|Note:|Explanation:).*$',
        '',
        code,
        flags=re.IGNORECASE | re.DOTALL
    )
    
    lines = code.split("\n")
    # Remove all lines that are just ``` or ```python or ```py etc.
    lines = [l for l in lines if not re.match(r'^```\w*\s*$', l.strip())]
    return "\n".join(lines).strip()


def _wrap_text(text, max_chars=55):
    """Break text into lines of at most max_chars at word boundaries."""
    lines = []
    words = text.split()
    current = ""
    for w in words:
        if current and len(current) + len(w) + 1 > max_chars:
            lines.append(current.strip())
            current = w
        else:
            current = (current + " " + w) if current else w
    if current:
        lines.append(current.strip())
    return lines


def _fallback_scene(topic, response_text):
    """Fallback scene with clean multi-line text layout."""
    # Clean markdown from response before using in Text() objects
    clean_text = _clean_response_text(response_text)
    clean_text = clean_text.replace('"', "'").replace("\n", " ").strip()

    # Split into slides — each slide has 2-3 short lines
    all_lines = _wrap_text(clean_text, max_chars=55)
    slides = []
    for i in range(0, len(all_lines), 3):
        slides.append(all_lines[i:i + 3])
    slides = slides[:6]  # Max 6 slides

    # Sanitize topic for use in generated Python strings
    safe_topic = topic.replace('\\', '\\\\').replace('"', "'")

    # Build scene code
    scene_lines = [
        'from manim import *',
        '',
        'class GeneratedScene(Scene):',
        '    def construct(self):',
        '        self.camera.background_color = "#0a1224"',
        '',
        '        # --- Title ---',
        f'        title = Text("{safe_topic}", font_size=36, weight=BOLD, color=BLUE_C)',
        '        if title.width > config.frame_width - 2:',
        '            title.scale_to_fit_width(config.frame_width - 2)',
        '        title.to_edge(UP, buff=0.6)',
        '        underline = Line(',
        '            LEFT * (config.frame_width / 2 - 1),',
        '            RIGHT * (config.frame_width / 2 - 1),',
        '            stroke_width=1, color=BLUE_C',
        '        )',
        '        underline.next_to(title, DOWN, buff=0.2)',
        '        self.play(Write(title), Create(underline))',
        '        self.wait(1)',
    ]

    body_colors = ['WHITE', 'GREY_A', 'WHITE', 'GREY_A', 'WHITE', 'GREY_A']

    for slide_idx, slide_lines in enumerate(slides):
        color = body_colors[slide_idx % len(body_colors)]
        step_label = f'step_{slide_idx}'
        group_name = f'slide_{slide_idx}'

        # Build Text objects for each line in this slide
        text_vars = []
        scene_lines.append('')
        scene_lines.append(f'        # --- Slide {slide_idx + 1} ---')

        # Step number indicator
        scene_lines.append(
            f'        {step_label} = Text("({slide_idx + 1}/{len(slides)})", '
            f'font_size=18, color=GREY_A)'
        )
        scene_lines.append(
            f'        {step_label}.to_corner(DR, buff=0.4)'
        )

        for line_idx, line_text in enumerate(slide_lines):
            safe_line = line_text.replace('\\', '\\\\').replace('"', "'").replace('{', '{{').replace('}', '}}')
            var = f'line_{slide_idx}_{line_idx}'
            text_vars.append(var)
            scene_lines.append(
                f'        {var} = Text("{safe_line}", font_size=24, color={color})'
            )
            scene_lines.append(
                f'        if {var}.width > config.frame_width - 2:'
            )
            scene_lines.append(
                f'            {var}.scale_to_fit_width(config.frame_width - 2)'
            )

        # Group the lines and center below title
        vars_joined = ', '.join(text_vars)
        scene_lines += [
            f'        {group_name} = VGroup({vars_joined}).arrange(DOWN, buff=0.35)',
            f'        {group_name}.next_to(underline, DOWN, buff=0.8)',
            f'        self.play(FadeIn({group_name}, shift=UP * 0.3), FadeIn({step_label}))',
            f'        self.wait(2.5)',
            f'        self.play(FadeOut({group_name}), FadeOut({step_label}))',
        ]

    scene_lines += [
        '',
        '        # --- End ---',
        '        self.play(FadeOut(*self.mobjects))',
        '        self.wait(0.5)',
    ]

    return '\n'.join(scene_lines)


def process_job(job_path):
    job_file = os.path.basename(job_path)
    lesson_id = job_file.replace(".json", "")
    job_start = time.time()
    
    # job_path is expected to be USER_DATA_ROOT/{user_id}/incoming_jobs/{lesson_id}.json
    user_dir = os.path.dirname(os.path.dirname(job_path)) 
    
    # Setup user-specific directories
    DONE = os.path.join(user_dir, "done_jobs")
    FAILED = os.path.join(user_dir, "failed_jobs")
    RENDERED = os.path.join(user_dir, "rendered_videos")
    SCENES_DIR = os.path.join(user_dir, "manim_scenes")
    
    for d in [DONE, FAILED, RENDERED, SCENES_DIR]:
        os.makedirs(d, exist_ok=True)

    try:
        # Check if video already exists (cache hit from backend)
        existing_video = os.path.join(RENDERED, f"{lesson_id}.mp4")
        if os.path.exists(existing_video):
            print(f"✓ Video already exists for {job_file}, skipping generation (cache hit)")
            shutil.move(job_path, os.path.join(DONE, job_file))
            return
        
        # Read job data
        with open(job_path) as f:
            job_data = json.load(f)

        topic = job_data.get("topic", "Lesson")
        response_text = job_data.get("response_text", "")

        if not response_text:
            raise ValueError("No response_text in job")

        # Generate manim code via Gemini
        print(f"Generating manim code for: {topic}")
        codegen_start = time.time()
        manim_code = generate_manim_code(topic, response_text)
        # Inject safety call inside construct()
        manim_code = manim_code.replace(  # type: ignore[union-attr]
            "def construct(self):",
            "def construct(self):\n        self.camera.background_color = '#0a1224'"
        )
        codegen_time = time.time() - codegen_start
        print(f"⏱  Code generation: {codegen_time:.1f}s")

        # Write the generated scene to a file
        scene_file = os.path.join(SCENES_DIR, f"{lesson_id}.py")
        with open(scene_file, "w") as f:
            f.write(manim_code)

        print(f"Running manim on generated scene...")

        # Run manim on the generated file (480p @ 10fps, single pass)
        render_start = time.time()
        result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "manim",
                    "-ql",
                    "--fps", "10",
                    scene_file,
                    "GeneratedScene",
                ],
                check=True,
                cwd=BASE,
                env={**os.environ, "PYTHONPATH": BASE},
                capture_output=True,
                text=True,
                timeout=120,
            )
        render_time = time.time() - render_start
        print(f"⏱  Manim render: {render_time:.1f}s")

        # Find the output video — manim outputs to media/videos/<filename>/1080p30/
        scene_name = lesson_id
        video_dir = os.path.join(
            MANIM_OUTPUT_DIR, scene_name, "480p10"
        )
        video_file = os.path.join(video_dir, "GeneratedScene.mp4")

        if os.path.exists(video_file):
            dest = os.path.join(RENDERED, f"{lesson_id}.mp4")
            shutil.copy2(video_file, dest)
            print(f"✓ Rendered {job_file} → {dest}")
        else:
            # Try to find it by searching
            print(f"Looking for video in {MANIM_OUTPUT_DIR}...")
            found = False
            for root, dirs, files in os.walk(MANIM_OUTPUT_DIR):
                for fname in files:
                    if fname == "GeneratedScene.mp4" and "partial" not in root:
                        src = os.path.join(root, fname)
                        dest = os.path.join(RENDERED, f"{lesson_id}.mp4")
                        shutil.copy2(src, dest)
                        print(f"✓ Rendered {job_file} → {dest}")
                        found = True
                        break
                if found:
                    break

            if not found:
                print(f"WARNING: Could not find rendered video for {lesson_id}")
                # pyre-ignore[16]
                print(f"Manim stdout: {result.stdout[-500:]}")

        if os.path.exists(job_path):
            shutil.move(job_path, os.path.join(DONE, job_file))
        total_time = time.time() - job_start
        print(f"⏱  Job done in {total_time:.1f}s (codegen: {codegen_time:.1f}s, render: {render_time:.1f}s)")

    except subprocess.CalledProcessError as e:
        print(f"Manim render failed for {job_file}:")
        print(f"  stderr: {e.stderr[-1000:] if e.stderr else 'none'}")

        # If it looks like a LaTeX error, try stripping MathTex first
        is_latex_error = e.stderr and ('latex error' in e.stderr.lower() or 'tex' in e.stderr.lower())
        if is_latex_error:
            try:
                print(f"LaTeX error detected — retrying with MathTex stripped...")
                stripped_code = _strip_mathtex_from_code(manim_code)
                scene_file_stripped = os.path.join(SCENES_DIR, f"{lesson_id}_notex.py")
                with open(scene_file_stripped, "w") as f:
                    f.write(stripped_code)
                result2 = subprocess.run(
                    [
                        "python3", "-m", "manim", "-ql",
                        "--fps", "10",
                        scene_file_stripped, "GeneratedScene",
                    ],
                    check=True,
                    cwd=BASE,
                    env={**os.environ, "PYTHONPATH": BASE},
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                # Find and copy the video
                for root, dirs, files in os.walk(MANIM_OUTPUT_DIR):
                    for fname in files:
                        if fname == "GeneratedScene.mp4" and "partial" not in root:
                            dest = os.path.join(RENDERED, f"{lesson_id}.mp4")
                            shutil.copy2(os.path.join(root, fname), dest)
                            print(f"✓ Rendered (no-LaTeX) {job_file} → {dest}")
                            shutil.move(job_path, os.path.join(DONE, job_file))
                            return
            except Exception as e_strip:
                print(f"MathTex-stripped retry also failed: {e_strip}")

        # If still here, try the simple fallback scene
        try:
            _render_fallback(job_file, job_path, lesson_id, job_data, user_dir)
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            shutil.move(job_path, os.path.join(FAILED, job_file))

    except Exception as e:
        print(f"Failed {job_file}: {e}")
        if os.path.exists(job_path):
            shutil.move(job_path, os.path.join(FAILED, job_file))


def _render_fallback(job_file, job_path, lesson_id, job_data, user_dir):
    """Attempt rendering with the simple fallback scene."""
    
    DONE = os.path.join(user_dir, "done_jobs")
    RENDERED = os.path.join(user_dir, "rendered_videos")
    SCENES_DIR = os.path.join(user_dir, "manim_scenes")
    
    print(f"Retrying {job_file} with fallback scene...")
    topic = job_data.get("topic", "Lesson")
    response_text = job_data.get("response_text", "")

    fallback_code = _fallback_scene(topic, response_text)
    scene_file = os.path.join(SCENES_DIR, f"{lesson_id}_fallback.py")
    with open(scene_file, "w") as f:
        f.write(fallback_code)

    subprocess.run(
        [
            "python3", "-m", "manim", "-ql",
            "--fps", "10",
            scene_file, "GeneratedScene",
        ],
        check=True,
        cwd=BASE,
        env={**os.environ, "PYTHONPATH": BASE},
        capture_output=True,
        text=True,
        timeout=120,
    )

    # Find and copy video
    for root, dirs, files in os.walk(MANIM_OUTPUT_DIR):
        for fname in files:
            if fname == "GeneratedScene.mp4" and "partial" not in root:
                dest = os.path.join(RENDERED, f"{lesson_id}.mp4")
                shutil.copy2(os.path.join(root, fname), dest)
                print(f"✓ Fallback rendered {job_file} → {dest}")
                shutil.move(job_path, os.path.join(DONE, job_file))
                return

    raise RuntimeError("Fallback video not found either")


def main():
    print("Renderer worker started")
    print(f"  Gemini model: {GEMINI_MODEL}")
    print(f"  API key set: {'yes' if GEMINI_API_KEY else 'NO'}")
    print(f"  Watching: {USER_DATA_ROOT}/*/incoming_jobs/")

    # Keep track of active jobs so we don't submit the same job twice
    active_jobs = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        while True:
            job_pattern = os.path.join(USER_DATA_ROOT, "*", "incoming_jobs", "*.json")
            for job_path in glob.glob(job_pattern):
                if job_path not in active_jobs:
                    active_jobs.add(job_path)
                    
                    def run_job(path: str) -> None:
                        try:
                            process_job(path)
                        except Exception as e:
                            print(f"Error processing job {path}: {e}")
                        finally:
                            active_jobs.discard(path)
                    
                    executor.submit(run_job, str(job_path))  # type: ignore[arg-type]
            time.sleep(2)

if __name__ == "__main__":
    main()
