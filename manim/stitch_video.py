import os
import subprocess

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(BASE_DIR, "media", "videos")
OUTPUT_FILE = os.path.join(BASE_DIR, "sqora_demo.mp4")

def stitch():
    print("Stitching scenes together...")
    
    # Find all GeneratedScene.mp4 files in the media dir
    # Path: media/videos/scene_1_intro/480p15/GeneratedScene.mp4
    scene_files = []
    
    # Sort by the scene name in the folder path
    def get_scene_index(name):
        try:
            return int(name.split('_')[1])
        except (IndexError, ValueError):
            return 999

    scene_names = sorted(
        [d for d in os.listdir(MEDIA_DIR) if d.startswith("scene_")],
        key=get_scene_index
    )
    for scene_name in scene_names:
        quality_dir = os.path.join(MEDIA_DIR, scene_name, "480p15")
        video_path = os.path.join(quality_dir, "GeneratedScene.mp4")
        
        if os.path.exists(video_path):
            scene_files.append(video_path)
            print(f"Adding: {scene_name}")
    
    if not scene_files:
        print("No videos found to stitch!")
        return
    
    # Create FFmpeg file list
    list_path = os.path.join(BASE_DIR, "concat_list.txt")
    with open(list_path, "w") as f:
        for fpath in scene_files:
            # Use absolute path and escape single quotes
            f.write(f"file '{fpath}'\n")
    
    # Run FFmpeg concat
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            OUTPUT_FILE
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        print(f"✓ Video successfully stitched to: {OUTPUT_FILE}")
        
        # Cleanup
        os.remove(list_path)
    except subprocess.CalledProcessError as e:
        print(f"✗ FFmpeg stitching failed: {e.stderr.decode()[-200:]}")

if __name__ == "__main__":
    stitch()
