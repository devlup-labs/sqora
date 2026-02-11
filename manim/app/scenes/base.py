from manim import *

class TeacherScene(Scene):
    def setup(self):
        # Premium blackboard background
        self.camera.background_color = "#0a1224"

        # Track screen state
        self.current_text = None
        self.current_equation = None

    # ---------------- TITLE ----------------
    def show_title(self, text):
        title = Text(
            text,
            font="Inter",
            font_size=44,
            weight=BOLD,
            color=BLUE_C
        )
        title.to_edge(UP).shift(DOWN * 0.3)

        underline = Line(
            title.get_left(),
            title.get_right(),
            stroke_width=2,
            color=BLUE_C
        ).next_to(title, DOWN, buff=0.15)

        self.play(Write(title), Create(underline))
        self.wait(0.5)

    # ---------------- EXPLANATION ----------------
    def show_explanation(self, text):
        if self.current_text:
            self.play(FadeOut(self.current_text))

        explanation = Text(
            text,
            font="Inter",
            font_size=26,
            line_spacing=1.0,
            width=11,
            color=GREY_A
        )

        # Explanation safe zone (BOTTOM)
        explanation.to_edge(DOWN).shift(UP * 0.4)

        self.play(FadeIn(explanation, shift=UP))
        self.wait(1.5)

        self.current_text = explanation

    # ---------------- EQUATION ----------------
    def show_equation(self, latex):
        if self.current_equation:
            self.play(FadeOut(self.current_equation))

        is_block = any(k in latex for k in ["aligned", "cases", "pmatrix"])

        eq = MathTex(
            latex,
            font_size=56 if is_block else 64,
            color=YELLOW_C
        )

        # Equation safe zone (CENTER)
        eq.move_to(ORIGIN).shift(UP * 0.3)

        self.play(Write(eq))
        self.wait(2)

        self.current_equation = eq

    # ---------------- CLEAR SCREEN ----------------
    def clear_all(self):
        animations = []
        if self.current_text:
            animations.append(FadeOut(self.current_text))
            self.current_text = None
        if self.current_equation:
            animations.append(FadeOut(self.current_equation))
            self.current_equation = None

        if animations:
            self.play(*animations)
