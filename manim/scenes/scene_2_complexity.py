from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *
import random

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        # Chaos
        dots = VGroup(*[Dot(point=[random.uniform(-5, 5), random.uniform(-3, 3), 0], color=random.choice([RED_C, YELLOW_C])) for _ in range(50)])
        text_chaos = get_body("From Chaos...")
        
        # Order
        grid = VGroup(*[Square(side_length=0.5, color=PRIMARY_COLOR).move_to([x, y, 0]) for x in range(-3, 4) for y in range(-2, 3)])
        text_order = get_body("To Clarity.")
        
        self.play(FadeIn(dots), Write(text_chaos.to_edge(UP)), run_time=1.5)
        self.wait(1)
        self.play(
            ReplacementTransform(dots, grid),
            ReplacementTransform(text_chaos, text_order.to_edge(UP)),
            run_time=2
        )
        self.wait(2)
        self.play(FadeOut(grid), FadeOut(text_order), run_time=0.5)

