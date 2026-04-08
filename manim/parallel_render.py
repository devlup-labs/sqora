import os
import subprocess
import concurrent.futures
import time

# Configuration
SCENES_DIR = os.path.join(os.path.dirname(__file__), "scenes")
VENV_PYTHON = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv", "bin", "python3"))
OUTPUT_QUALITY = "-ql"  # Low quality for speed
FPS = "15"

def render_scene(file_name):
    file_path = os.path.join(SCENES_DIR, file_name)
    start_time = time.time()
    print(f"Starting render for {file_name}...")
    
    try:
        # Command: python3 -m manim -ql --fps 15 <file_path> GeneratedScene
        cmd = [
            VENV_PYTHON, "-m", "manim",
            OUTPUT_QUALITY,
            "--fps", FPS,
            file_path,
            "GeneratedScene",
            "--media_dir", os.path.join(os.path.dirname(__file__), "media")
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        duration = time.time() - start_time
        print(f"✓ Finished {file_name} in {duration:.1f}s")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed {file_name}: {e.stderr[-200:]}")
        return False

def main():
    scene_files = sorted([f for f in os.listdir(SCENES_DIR) if f.startswith("scene_") and f.endswith(".py")])
    print(f"Starting parallel render of {len(scene_files)} scenes...")
    
    start_total = time.time()
    
    # Render all scenes in parallel using all available cores
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        results = list(executor.map(render_scene, scene_files))
    
    total_duration = time.time() - start_total
    success_count = sum(1 for r in results if r)
    
    print("\n" + "="*40)
    print(f"Parallel Render Complete: {success_count}/{len(scene_files)} success")
    print(f"Total time elapsed: {total_duration:.1f}s")
    print("="*40)

if __name__ == "__main__":
    main()
