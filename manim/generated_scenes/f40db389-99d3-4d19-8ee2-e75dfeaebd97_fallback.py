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

        body_0 = Text("In the simplest terms, Angular Momentum ($L$) is the 'quantity of rotation' an object has. If Linear Momentum ($p = mv$)", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_0, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_0))

        body_1 = Text("tells you how hard it is to stop an object moving in a straight line, Angular Momentum tells you how hard it is to stop", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_1, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_1))

        body_2 = Text("a rotating object. For your JEE/NEET prep, you need to look at it in two ways: for a point mass and for a rigid body.", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_2, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_2))

        body_3 = Text("--- For a Point Mass (Moving in a path) If a particle of mass $m$ is moving with velocity $v$ at a distance $r$ from a", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_3, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_3))

        body_4 = Text("fixed point, its angular momentum is: $$\\vec{{L}} = \\vec{{r}} \\times \\vec{{p}} = m(\\vec{{r}} \\times \\vec{{v}})$$ Magnitude: $L =", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_4, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_4))

        body_5 = Text("mvr \\sin\\theta$ (Shortcut: $L = m \\times v \\times r{{\\perp}}$, where $r{{\\perp}}$ is the perpendicular distance from the", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_5, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_5))

        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)