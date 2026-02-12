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

        body_0 = Text("In the world of Physics, Potential Energy (PE) is often called 'Stored Energy.' While Kinetic Energy is the energy of", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_0, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_0))

        body_1 = Text("motion, Potential Energy is the energy an object has because of its position or configuration. Think of it like a bank", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_1, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_1))

        body_2 = Text("account: you’ve stored energy there, and it’s ready to be 'spent' (converted into motion) whenever you need it! ---", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_2, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_2))

        body_3 = Text("Gravitational Potential Energy This is the most common type you’ll see in JEE/NEET problems. It is the energy an object", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_3, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_3))

        body_4 = Text("possesses because of its height above the ground. Formula: $$U = mgh$$ $m$: Mass of the object (kg) $g$: Acceleration", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_4, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_4))

        body_5 = Text("due to gravity ($\\approx 9.8$ or $10 \\text{{ m/s}}^2$) $h$: Height from the Reference Level (m) Important Concept: The", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_5, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_5))

        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)