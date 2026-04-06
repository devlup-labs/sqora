from manim import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = '#0a1224'
        self.camera.background_color = "#0a1224"

        # --- Title ---
        title = Text("JEE/NEET Lesson", font_size=36, weight=BOLD, color=BLUE_C)
        if title.width > config.frame_width - 2:
            title.scale_to_fit_width(config.frame_width - 2)
        title.to_edge(UP, buff=0.6)
        underline = Line(
            LEFT * (config.frame_width / 2 - 1),
            RIGHT * (config.frame_width / 2 - 1),
            stroke_width=1, color=BLUE_C
        )
        underline.next_to(title, DOWN, buff=0.2)
        self.play(Write(title), Create(underline))
        self.wait(1)

        # --- Slide 1 ---
        step_0 = Text("(1/3)", font_size=18, color=GREY_A)
        step_0.to_corner(DR, buff=0.4)
        line_0_0 = Text("Hey there! 👋 'Suhan' is a beautiful name, often used in", font_size=24, color=WHITE)
        if line_0_0.width > config.frame_width - 2:
            line_0_0.scale_to_fit_width(config.frame_width - 2)
        line_0_1 = Text("India. It's not a term you'll find in your JEE/NEET", font_size=24, color=WHITE)
        if line_0_1.width > config.frame_width - 2:
            line_0_1.scale_to_fit_width(config.frame_width - 2)
        line_0_2 = Text("syllabus, but I can tell you its meaning! Suhan (सुहान)", font_size=24, color=WHITE)
        if line_0_2.width > config.frame_width - 2:
            line_0_2.scale_to_fit_width(config.frame_width - 2)
        slide_0 = VGroup(line_0_0, line_0_1, line_0_2).arrange(DOWN, buff=0.35)
        slide_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_0, shift=UP * 0.3), FadeIn(step_0))
        self.wait(2.5)
        self.play(FadeOut(slide_0), FadeOut(step_0))

        # --- Slide 2 ---
        step_1 = Text("(2/3)", font_size=18, color=GREY_A)
        step_1.to_corner(DR, buff=0.4)
        line_1_0 = Text("typically means: Very pleasant Beautiful Charming", font_size=24, color=GREY_A)
        if line_1_0.width > config.frame_width - 2:
            line_1_0.scale_to_fit_width(config.frame_width - 2)
        line_1_1 = Text("Lovely It's a name that evokes positive and attractive", font_size=24, color=GREY_A)
        if line_1_1.width > config.frame_width - 2:
            line_1_1.scale_to_fit_width(config.frame_width - 2)
        line_1_2 = Text("qualities. Now, coming back to our studies, do you have", font_size=24, color=GREY_A)
        if line_1_2.width > config.frame_width - 2:
            line_1_2.scale_to_fit_width(config.frame_width - 2)
        slide_1 = VGroup(line_1_0, line_1_1, line_1_2).arrange(DOWN, buff=0.35)
        slide_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_1, shift=UP * 0.3), FadeIn(step_1))
        self.wait(2.5)
        self.play(FadeOut(slide_1), FadeOut(step_1))

        # --- Slide 3 ---
        step_2 = Text("(3/3)", font_size=18, color=GREY_A)
        step_2.to_corner(DR, buff=0.4)
        line_2_0 = Text("any questions about Physics, Chemistry, Biology, or", font_size=24, color=WHITE)
        if line_2_0.width > config.frame_width - 2:
            line_2_0.scale_to_fit_width(config.frame_width - 2)
        line_2_1 = Text("Maths that I can help you with for your JEE/NEET prep?", font_size=24, color=WHITE)
        if line_2_1.width > config.frame_width - 2:
            line_2_1.scale_to_fit_width(config.frame_width - 2)
        line_2_2 = Text("Let's ace those concepts! 💪", font_size=24, color=WHITE)
        if line_2_2.width > config.frame_width - 2:
            line_2_2.scale_to_fit_width(config.frame_width - 2)
        slide_2 = VGroup(line_2_0, line_2_1, line_2_2).arrange(DOWN, buff=0.35)
        slide_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_2, shift=UP * 0.3), FadeIn(step_2))
        self.wait(2.5)
        self.play(FadeOut(slide_2), FadeOut(step_2))

        # --- End ---
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)