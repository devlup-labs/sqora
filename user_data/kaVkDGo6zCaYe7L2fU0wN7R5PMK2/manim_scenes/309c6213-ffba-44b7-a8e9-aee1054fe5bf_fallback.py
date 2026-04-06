from manim import *

class GeneratedScene(Scene):
    def construct(self):
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
        step_0 = Text("(1/5)", font_size=18, color=GREY_A)
        step_0.to_corner(DR, buff=0.4)
        line_0_0 = Text("Alright, let's get straight to it! Newton's Third Law", font_size=24, color=WHITE)
        if line_0_0.width > config.frame_width - 2:
            line_0_0.scale_to_fit_width(config.frame_width - 2)
        line_0_1 = Text("of Motion: 'For every action, there is an equal and", font_size=24, color=WHITE)
        if line_0_1.width > config.frame_width - 2:
            line_0_1.scale_to_fit_width(config.frame_width - 2)
        line_0_2 = Text("opposite reaction.' In simpler terms: Whenever one", font_size=24, color=WHITE)
        if line_0_2.width > config.frame_width - 2:
            line_0_2.scale_to_fit_width(config.frame_width - 2)
        slide_0 = VGroup(line_0_0, line_0_1, line_0_2).arrange(DOWN, buff=0.35)
        slide_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_0, shift=UP * 0.3), FadeIn(step_0))
        self.wait(2.5)
        self.play(FadeOut(slide_0), FadeOut(step_0))

        # --- Slide 2 ---
        step_1 = Text("(2/5)", font_size=18, color=GREY_A)
        step_1.to_corner(DR, buff=0.4)
        line_1_0 = Text("object exerts a force on a second object (the", font_size=24, color=GREY_A)
        if line_1_0.width > config.frame_width - 2:
            line_1_0.scale_to_fit_width(config.frame_width - 2)
        line_1_1 = Text("'action'), the second object simultaneously exerts an", font_size=24, color=GREY_A)
        if line_1_1.width > config.frame_width - 2:
            line_1_1.scale_to_fit_width(config.frame_width - 2)
        line_1_2 = Text("equal force in the opposite direction on the first", font_size=24, color=GREY_A)
        if line_1_2.width > config.frame_width - 2:
            line_1_2.scale_to_fit_width(config.frame_width - 2)
        slide_1 = VGroup(line_1_0, line_1_1, line_1_2).arrange(DOWN, buff=0.35)
        slide_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_1, shift=UP * 0.3), FadeIn(step_1))
        self.wait(2.5)
        self.play(FadeOut(slide_1), FadeOut(step_1))

        # --- Slide 3 ---
        step_2 = Text("(3/5)", font_size=18, color=GREY_A)
        step_2.to_corner(DR, buff=0.4)
        line_2_0 = Text("object (the 'reaction'). Key points: Forces come in", font_size=24, color=WHITE)
        if line_2_0.width > config.frame_width - 2:
            line_2_0.scale_to_fit_width(config.frame_width - 2)
        line_2_1 = Text("pairs. You can't have one without the other. Equal in", font_size=24, color=WHITE)
        if line_2_1.width > config.frame_width - 2:
            line_2_1.scale_to_fit_width(config.frame_width - 2)
        line_2_2 = Text("magnitude, opposite in direction. Act on different*", font_size=24, color=WHITE)
        if line_2_2.width > config.frame_width - 2:
            line_2_2.scale_to_fit_width(config.frame_width - 2)
        slide_2 = VGroup(line_2_0, line_2_1, line_2_2).arrange(DOWN, buff=0.35)
        slide_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_2, shift=UP * 0.3), FadeIn(step_2))
        self.wait(2.5)
        self.play(FadeOut(slide_2), FadeOut(step_2))

        # --- Slide 4 ---
        step_3 = Text("(4/5)", font_size=18, color=GREY_A)
        step_3.to_corner(DR, buff=0.4)
        line_3_0 = Text("objects. (This is crucial!) Example: When you push a", font_size=24, color=GREY_A)
        if line_3_0.width > config.frame_width - 2:
            line_3_0.scale_to_fit_width(config.frame_width - 2)
        line_3_1 = Text("wall (action force), the wall pushes back on you with", font_size=24, color=GREY_A)
        if line_3_1.width > config.frame_width - 2:
            line_3_1.scale_to_fit_width(config.frame_width - 2)
        line_3_2 = Text("an equal and opposite force (reaction force). You feel", font_size=24, color=GREY_A)
        if line_3_2.width > config.frame_width - 2:
            line_3_2.scale_to_fit_width(config.frame_width - 2)
        slide_3 = VGroup(line_3_0, line_3_1, line_3_2).arrange(DOWN, buff=0.35)
        slide_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_3, shift=UP * 0.3), FadeIn(step_3))
        self.wait(2.5)
        self.play(FadeOut(slide_3), FadeOut(step_3))

        # --- Slide 5 ---
        step_4 = Text("(5/5)", font_size=18, color=GREY_A)
        step_4.to_corner(DR, buff=0.4)
        line_4_0 = Text("the wall pushing back!", font_size=24, color=WHITE)
        if line_4_0.width > config.frame_width - 2:
            line_4_0.scale_to_fit_width(config.frame_width - 2)
        slide_4 = VGroup(line_4_0).arrange(DOWN, buff=0.35)
        slide_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_4, shift=UP * 0.3), FadeIn(step_4))
        self.wait(2.5)
        self.play(FadeOut(slide_4), FadeOut(step_4))

        # --- End ---
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)