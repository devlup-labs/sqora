from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        shield = Polygon([-1, 1, 0], [1, 1, 0], [1, -0.5, 0], [0, -1.5, 0], [-1, -0.5, 0], color=BLUE_B, fill_opacity=0.3)
        check = Tex(r"\checkmark", color=GREEN_C).scale(2).move_to(shield)
        
        text = get_title("Enterprise Security")
        
        self.play(Create(shield), run_time=1)
        scan_line = Line(LEFT*2, RIGHT*2, color=BLUE_A, stroke_width=4).move_to(shield).shift(UP*1.5)
        
        self.play(FadeIn(scan_line), run_time=0.5)
        self.play(scan_line.animate.shift(DOWN*3), run_time=1.5, rate_func=linear)
        self.play(FadeIn(check, scale=0.5), FadeOut(scan_line), run_time=0.5)
        self.play(Write(text.to_edge(UP)), run_time=1)
        
        self.wait(2)
        self.play(FadeOut(shield), FadeOut(check), FadeOut(text), run_time=0.5)

