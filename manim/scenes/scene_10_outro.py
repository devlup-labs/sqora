from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        text1 = get_title("Join the Revolution")
        logo = Circle(radius=1, color=PRIMARY_COLOR, fill_opacity=0.5).shift(UP*0.5)
        text2 = get_title("SQORA.IO", color=SECONDARY_COLOR).next_to(logo, DOWN, buff=1)
        
        self.play(Write(text1), run_time=1.5)
        self.wait(1)
        self.play(ReplacementTransform(text1, logo), FadeIn(text2, shift=UP*0.3), run_time=1.5)
        
        self.play(logo.animate.scale(1.2), rate_func=there_and_back, run_time=2)
        self.wait(3)
        self.play(FadeOut(VGroup(logo, text2)), run_time=1)

