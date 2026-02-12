from manim import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = "#0a1224"

        title = Text("JEE/NEET Lesson", font_size=44, weight=BOLD, color=BLUE_C)
        title.to_edge(UP).shift(DOWN * 0.3)
        underline = Line(title.get_left(), title.get_right(), stroke_width=2, color=BLUE_C)
        underline.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Create(underline))
        self.wait(1)

        body = Text("Hello! Newton's Laws of Motion are the **bread and butter of Mechanics**. For JEE and NEET, these laws aren't just definitions—they are tools you will use to solve almost every physics problem.  Let’s...", font_size=22, color=GREY_A, line_spacing=1.0)
        body.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body, shift=UP))
        self.wait(3)
