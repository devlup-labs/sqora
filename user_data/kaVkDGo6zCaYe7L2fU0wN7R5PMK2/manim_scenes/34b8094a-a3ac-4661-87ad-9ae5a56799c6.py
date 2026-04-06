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
        line_0_0 = Text("Hey there! Let's break down entropy in a simple way.", font_size=24, color=WHITE)
        if line_0_0.width > config.frame_width - 2:
            line_0_0.scale_to_fit_width(config.frame_width - 2)
        line_0_1 = Text("Entropy is basically a measure of the 'disorder' or", font_size=24, color=WHITE)
        if line_0_1.width > config.frame_width - 2:
            line_0_1.scale_to_fit_width(config.frame_width - 2)
        line_0_2 = Text("'randomness' in a system. Think of it like this: Your", font_size=24, color=WHITE)
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
        line_1_0 = Text("Room Example: When your room is perfectly tidy,", font_size=24, color=GREY_A)
        if line_1_0.width > config.frame_width - 2:
            line_1_0.scale_to_fit_width(config.frame_width - 2)
        line_1_1 = Text("everything in its place, it has low entropy (low", font_size=24, color=GREY_A)
        if line_1_1.width > config.frame_width - 2:
            line_1_1.scale_to_fit_width(config.frame_width - 2)
        line_1_2 = Text("disorder). When your room is messy, clothes everywhere,", font_size=24, color=GREY_A)
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
        line_2_0 = Text("books scattered, it has high entropy (high disorder).", font_size=24, color=WHITE)
        if line_2_0.width > config.frame_width - 2:
            line_2_0.scale_to_fit_width(config.frame_width - 2)
        line_2_1 = Text("Nature tends to move towards higher entropy – your room", font_size=24, color=WHITE)
        if line_2_1.width > config.frame_width - 2:
            line_2_1.scale_to_fit_width(config.frame_width - 2)
        line_2_2 = Text("gets messy on its own, right? You have to put effort to", font_size=24, color=WHITE)
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
        line_3_0 = Text("make it tidy! States of Matter: Solids: Particles are", font_size=24, color=GREY_A)
        if line_3_0.width > config.frame_width - 2:
            line_3_0.scale_to_fit_width(config.frame_width - 2)
        line_3_1 = Text("tightly packed and arranged in a very ordered way. So,", font_size=24, color=GREY_A)
        if line_3_1.width > config.frame_width - 2:
            line_3_1.scale_to_fit_width(config.frame_width - 2)
        line_3_2 = Text("solids have low entropy. Liquids: Particles can move", font_size=24, color=GREY_A)
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
        line_4_0 = Text("around more freely, so there's more disorder than in", font_size=24, color=WHITE)
        if line_4_0.width > config.frame_width - 2:
            line_4_0.scale_to_fit_width(config.frame_width - 2)
        line_4_1 = Text("solids. Liquids have medium entropy. Gases: Particles", font_size=24, color=WHITE)
        if line_4_1.width > config.frame_width - 2:
            line_4_1.scale_to_fit_width(config.frame_width - 2)
        line_4_2 = Text("are flying all over the place, very spread out and", font_size=24, color=WHITE)
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
        line_5_0 = Text("disordered. Gases have the highest entropy. Example:", font_size=24, color=GREY_A)
        if line_5_0.width > config.frame_width - 2:
            line_5_0.scale_to_fit_width(config.frame_width - 2)
        line_5_1 = Text("When ice melts into water, or water boils into steam,", font_size=24, color=GREY_A)
        if line_5_1.width > config.frame_width - 2:
            line_5_1.scale_to_fit_width(config.frame_width - 2)
        line_5_2 = Text("the entropy increases because the particles become more", font_size=24, color=GREY_A)
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