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

        body_0 = Text("To understand Moment of Inertia ($I$), think of it as the 'Rotational version of Mass.' In linear motion, Mass is the", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_0, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_0))

        body_1 = Text("'laziness' of an object to change its state of rest or motion. In rotational motion, Moment of Inertia is the", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_1, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_1))

        body_2 = Text("'rotational laziness'—it tells us how difficult it is to start an object spinning or to stop it once it’s already", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_2, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_2))

        body_3 = Text("spinning. --- The Basic Formula For a single point mass ($m$) at a distance ($r$) from the axis of rotation: $$I =", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_3, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_3))

        body_4 = Text("mr^2$$ For a system of many particles: $$I = m1r1^2 + m2r2^2 + m3r3^2 + ...$$ Units: $\\text{{kg}}\\cdot\\text{{m}}^2$", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_4, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_4))

        body_5 = Text("Dimensional Formula: $[ML^2T^0]$ --- What does it depend on? Unlike mass (which stays the same no matter how you move an", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_5, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_5))

        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)