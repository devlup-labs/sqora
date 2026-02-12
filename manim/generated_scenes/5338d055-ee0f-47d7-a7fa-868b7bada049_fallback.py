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

        body_0 = Text("This is probably the most famous equation in the world! Proposed by **Albert Einstein** in 1905, it changed how we", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_0.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_0, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_0))

        body_1 = Text("understand the universe. For your JEE/NEET syllabus, this formula is the heart of **Modern Physics**, specifically in", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_1.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_1, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_1))

        body_2 = Text("the **'Atoms and Nuclei'** chapter. --- ### What do the letters mean? $$E = mc^2$$ * **$E$ (Energy):** The total energy", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_2.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_2, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_2))

        body_3 = Text("contained within an object. * **$m$ (Mass):** The mass of the object. * **$c$ (Speed of Light):** A constant value,", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_3.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_3, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_3))

        body_4 = Text("approximately **$3 \times 10^8$ m/s**. ### What does it actually tell us? It tells us that **Mass and Energy are the", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_4.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_4, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_4))

        body_5 = Text("same thing**, just in different forms. Mass is basically 'highly concentrated energy.' Because the speed of light ($c$)", font_size=28, color=GREY_A, width=config.frame_width - 2)
        body_5.next_to(underline, DOWN, buff=0.8)
        self.play(FadeIn(body_5, shift=UP))
        self.wait(2)
        self.play(FadeOut(body_5))

        self.play(FadeOut(*self.mobjects))
        self.wait(0.5)