from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        # Complex machine (simplified)
        gears = VGroup(*[RegularPolygon(n=8, color=GREY_C).scale(0.4).shift([x, y, 0]) for x in range(-2, 3) for y in range(-1, 2)])
        text_complex = get_body("Complex Workflows...")
        
        button = RoundedRectangle(corner_radius=0.5, height=1.5, width=4, color=BLUE_C, fill_opacity=1)
        btn_text = Text("SIMPLIFY", color=WHITE, font_size=36).move_to(button)
        easy_ui = VGroup(button, btn_text)
        
        self.play(FadeIn(gears), Write(text_complex.to_edge(UP)), run_time=1)
        self.play(gears.animate.rotate(PI/2), run_time=2)
        self.wait(0.5)
        
        self.play(
            ReplacementTransform(gears, button),
            ReplacementTransform(text_complex, btn_text),
            run_time=1.5
        )
        self.play(button.animate.set_color(GREEN_C), run_time=0.5)
        self.wait(2)
        self.play(FadeOut(easy_ui), run_time=0.5)

