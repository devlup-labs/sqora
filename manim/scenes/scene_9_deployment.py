from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        cloud = VGroup(
            Circle(radius=0.8).shift(LEFT*0.5),
            Circle(radius=1.0).shift(ORIGIN),
            Circle(radius=0.8).shift(RIGHT*0.5),
            Rectangle(height=1.0, width=1.5).shift(DOWN*0.3)
        ).set_fill(WHITE, opacity=1).set_stroke(GREY_B, width=2)
        
        arrow = Arrow(DOWN*0.5, UP*1.5, color=GREEN_C, stroke_width=8)
        text = get_title("Deploy Instantly")
        
        self.play(FadeIn(cloud, shift=UP*0.5), run_time=1)
        self.play(FadeIn(arrow, shift=UP*1), run_time=1)
        self.play(Write(text.to_edge(DOWN)), run_time=1)
        
        self.play(arrow.animate.shift(UP*0.5), rate_func=there_and_back, run_time=1)
        self.wait(2)
        self.play(FadeOut(cloud), FadeOut(arrow), FadeOut(text), run_time=0.5)

