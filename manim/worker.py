import os
import time
import shutil
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))

INCOMING = os.path.join(BASE, "jobs/incoming")
DONE = os.path.join(BASE, "jobs/done")
FAILED = os.path.join(BASE, "jobs/failed")

def process_job(job_file):
    job_path = os.path.join(INCOMING, job_file)

    try:
        subprocess.run(
            [
                "manim",
                "-pql",
                "app/scenes/lesson.py",
                "LessonScene"
            ],
            check=True,
            cwd=BASE,
            env={**os.environ, "LESSON_FILE": job_path}
        )

        shutil.move(job_path, os.path.join(DONE, job_file))
        print(f"Rendered {job_file}")

    except Exception as e:
        shutil.move(job_path, os.path.join(FAILED, job_file))
        print(f"Failed {job_file}: {e}")

def main():
    print("Renderer worker started")
    while True:
        for file in os.listdir(INCOMING):
            if file.endswith(".json"):
                process_job(file)
        time.sleep(2)

if __name__ == "__main__":
    main()
