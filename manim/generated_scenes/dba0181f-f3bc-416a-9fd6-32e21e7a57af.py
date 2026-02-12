from manim import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = "#0a1224"

        title = Text("JEE/NEET Lesson", font_size=40, weight=BOLD, color=BLUE_C)
        title.width = min(title.width, config.frame_width - 2)
        title.to_edge(UP).shift(DOWN * 0.3)
        underline = Line(title.get_left(), title.get_right(), stroke_width=2, color=BLUE_C)
        underline.next_to(title, DOWN, buff=0.15)
        self.play(Write(title), Create(underline))
        self.wait(1)

        body_0 = Text("Great question! Rainbows are a beautiful combination of three major physics phenomena: **Refraction, Dispersion, and", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_0, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_0))

        body_1 = Text("Internal Reflection.** For your JEE/NEET prep, you should think of a **raindrop as a tiny glass prism.** --- ### The 3", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_1, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_1))

        body_2 = Text("Steps to a Rainbow To see a rainbow, you need two things: **The Sun behind you** and **Raindrops in front of you.** Here", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_2, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_2))

        body_3 = Text("is what happens inside a single drop: #### 1. Refraction and Dispersion (Entry) As sunlight enters the raindrop, it", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_3, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_3))

        body_4 = Text("slows down and bends (this is **Refraction**). But white light is made of 7 colors (VIBGYOR). Each color bends at a", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_4, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_4))

        body_5 = Text("slightly different angle—**Violet bends the most, and Red bends the least.** This splitting of light is called", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_5, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_5))

        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)