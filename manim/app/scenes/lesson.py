import os
import json
from app.scenes.base import TeacherScene

class LessonScene(TeacherScene):
    def construct(self):
        lesson_file = os.environ.get("LESSON_FILE")

        if not lesson_file:
            raise ValueError("No LESSON_FILE provided")

        with open(lesson_file) as f:
            data = json.load(f)

        self.show_title(data["topic"])

        for section in data["sections"]:
            if section["type"] == "explanation":
                self.show_explanation(section["content"])
            elif section["type"] == "equation":
                self.show_equation(section["content"])
            elif section["type"] == "conclusion":
                self.clear_all()
                self.show_explanation(section["content"])

        self.wait(2)
