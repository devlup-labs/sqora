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
        step_0 = Text("(1/6)", font_size=18, color=GREY_A)
        step_0.to_corner(DR, buff=0.4)
        line_0_0 = Text("Hey there! Let's break down Newton's First Law of", font_size=24, color=WHITE)
        if line_0_0.width > config.frame_width - 2:
            line_0_0.scale_to_fit_width(config.frame_width - 2)
        line_0_1 = Text("Motion, also known as the Law of Inertia, in a simple", font_size=24, color=WHITE)
        if line_0_1.width > config.frame_width - 2:
            line_0_1.scale_to_fit_width(config.frame_width - 2)
        line_0_2 = Text("way. Newton's First Law states: 'An object at rest will", font_size=24, color=WHITE)
        if line_0_2.width > config.frame_width - 2:
            line_0_2.scale_to_fit_width(config.frame_width - 2)
        slide_0 = VGroup(line_0_0, line_0_1, line_0_2).arrange(DOWN, buff=0.35)
        slide_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_0, shift=UP * 0.3), FadeIn(step_0))
        self.wait(2.5)
        self.play(FadeOut(slide_0), FadeOut(step_0))

        # --- Slide 2 ---
        step_1 = Text("(2/6)", font_size=18, color=GREY_A)
        step_1.to_corner(DR, buff=0.4)
        line_1_0 = Text("stay at rest, and an object in motion will stay in", font_size=24, color=GREY_A)
        if line_1_0.width > config.frame_width - 2:
            line_1_0.scale_to_fit_width(config.frame_width - 2)
        line_1_1 = Text("motion with the same speed and in the same direction,", font_size=24, color=GREY_A)
        if line_1_1.width > config.frame_width - 2:
            line_1_1.scale_to_fit_width(config.frame_width - 2)
        line_1_2 = Text("unless acted upon by an unbalanced external force.' In", font_size=24, color=GREY_A)
        if line_1_2.width > config.frame_width - 2:
            line_1_2.scale_to_fit_width(config.frame_width - 2)
        slide_1 = VGroup(line_1_0, line_1_1, line_1_2).arrange(DOWN, buff=0.35)
        slide_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_1, shift=UP * 0.3), FadeIn(step_1))
        self.wait(2.5)
        self.play(FadeOut(slide_1), FadeOut(step_1))

        # --- Slide 3 ---
        step_2 = Text("(3/6)", font_size=18, color=GREY_A)
        step_2.to_corner(DR, buff=0.4)
        line_2_0 = Text("simpler terms: If something isn't moving (like a book", font_size=24, color=WHITE)
        if line_2_0.width > config.frame_width - 2:
            line_2_0.scale_to_fit_width(config.frame_width - 2)
        line_2_1 = Text("on a table), it won't start moving on its own. If", font_size=24, color=WHITE)
        if line_2_1.width > config.frame_width - 2:
            line_2_1.scale_to_fit_width(config.frame_width - 2)
        line_2_2 = Text("something is moving (like a ball rolling), it won't", font_size=24, color=WHITE)
        if line_2_2.width > config.frame_width - 2:
            line_2_2.scale_to_fit_width(config.frame_width - 2)
        slide_2 = VGroup(line_2_0, line_2_1, line_2_2).arrange(DOWN, buff=0.35)
        slide_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_2, shift=UP * 0.3), FadeIn(step_2))
        self.wait(2.5)
        self.play(FadeOut(slide_2), FadeOut(step_2))

        # --- Slide 4 ---
        step_3 = Text("(4/6)", font_size=18, color=GREY_A)
        step_3.to_corner(DR, buff=0.4)
        line_3_0 = Text("stop or change its direction or speed on its own. Both", font_size=24, color=GREY_A)
        if line_3_0.width > config.frame_width - 2:
            line_3_0.scale_to_fit_width(config.frame_width - 2)
        line_3_1 = Text("of these will only happen if some net force (like a", font_size=24, color=GREY_A)
        if line_3_1.width > config.frame_width - 2:
            line_3_1.scale_to_fit_width(config.frame_width - 2)
        line_3_2 = Text("push, pull, or friction) acts on them. Key takeaway:", font_size=24, color=GREY_A)
        if line_3_2.width > config.frame_width - 2:
            line_3_2.scale_to_fit_width(config.frame_width - 2)
        slide_3 = VGroup(line_3_0, line_3_1, line_3_2).arrange(DOWN, buff=0.35)
        slide_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_3, shift=UP * 0.3), FadeIn(step_3))
        self.wait(2.5)
        self.play(FadeOut(slide_3), FadeOut(step_3))

        # --- Slide 5 ---
        step_4 = Text("(5/6)", font_size=18, color=GREY_A)
        step_4.to_corner(DR, buff=0.4)
        line_4_0 = Text("Objects resist changes to their state of motion. This", font_size=24, color=WHITE)
        if line_4_0.width > config.frame_width - 2:
            line_4_0.scale_to_fit_width(config.frame_width - 2)
        line_4_1 = Text("resistance is called Inertia. Example: Imagine a", font_size=24, color=WHITE)
        if line_4_1.width > config.frame_width - 2:
            line_4_1.scale_to_fit_width(config.frame_width - 2)
        line_4_2 = Text("cricket ball lying still on the pitch. It will stay", font_size=24, color=WHITE)
        if line_4_2.width > config.frame_width - 2:
            line_4_2.scale_to_fit_width(config.frame_width - 2)
        slide_4 = VGroup(line_4_0, line_4_1, line_4_2).arrange(DOWN, buff=0.35)
        slide_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_4, shift=UP * 0.3), FadeIn(step_4))
        self.wait(2.5)
        self.play(FadeOut(slide_4), FadeOut(step_4))

        # --- Slide 6 ---
        step_5 = Text("(6/6)", font_size=18, color=GREY_A)
        step_5.to_corner(DR, buff=0.4)
        line_5_0 = Text("there forever unless a player kicks it (an unbalanced", font_size=24, color=GREY_A)
        if line_5_0.width > config.frame_width - 2:
            line_5_0.scale_to_fit_width(config.frame_width - 2)
        line_5_1 = Text("force) or the wind blows it. Similarly, if you roll a", font_size=24, color=GREY_A)
        if line_5_1.width > config.frame_width - 2:
            line_5_1.scale_to_fit_width(config.frame_width - 2)
        line_5_2 = Text("ball on a perfectly frictionless surface, it would keep", font_size=24, color=GREY_A)
        if line_5_2.width > config.frame_width - 2:
            line_5_2.scale_to_fit_width(config.frame_width - 2)
        slide_5 = VGroup(line_5_0, line_5_1, line_5_2).arrange(DOWN, buff=0.35)
        slide_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(slide_5, shift=UP * 0.3), FadeIn(step_5))
        self.wait(2.5)
        self.play(FadeOut(slide_5), FadeOut(step_5))

        # --- End ---
        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)