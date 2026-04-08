from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        rocket = Triangle(color=WHITE, fill_opacity=1).scale(0.5).rotate(-PI/2)
        flame = Triangle(color=ORANGE, fill_opacity=0.8).scale(0.3).rotate(PI/2).next_to(rocket, LEFT, buff=0)
        ship = VGroup(rocket, flame)
        
        lines = VGroup(*[Line(LEFT*7, RIGHT*7, stroke_width=2, color=BLUE_E).shift(UP*i) for i in range(-3, 4)])
        
        text = get_title("10x Faster Rendering", color=SECONDARY_COLOR)
        
        self.add(lines)
        self.play(FadeIn(ship, shift=RIGHT*2), Write(text.to_edge(DOWN)), run_time=1)
        
        # Speed effect
        self.play(
            ship.animate.shift(RIGHT*10),
            lines.animate.shift(LEFT*5),
            rate_func=linear,
            run_time=3
        )
        self.wait(1)
        self.play(FadeOut(text), FadeOut(lines), run_time=0.5)

