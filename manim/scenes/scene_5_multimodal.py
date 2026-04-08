from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        video_icon = Square(color=BLUE_C).scale(0.5).shift(LEFT*3 + UP*1)
        audio_icon = Circle(color=GREEN_C).scale(0.5).shift(DOWN*2)
        text_icon = Triangle(color=YELLOW_C).scale(0.5).shift(RIGHT*3 + UP*1)
        
        center_node = Star(color=WHITE).scale(1.2)
        
        self.play(FadeIn(video_icon), FadeIn(audio_icon), FadeIn(text_icon), run_time=1)
        
        # Converge
        self.play(
            video_icon.animate.move_to(ORIGIN).set_opacity(0),
            audio_icon.animate.move_to(ORIGIN).set_opacity(0),
            text_icon.animate.move_to(ORIGIN).set_opacity(0),
            FadeIn(center_node, scale=0.5),
            run_time=2
        )
        
        label = get_body("Multi-Modal Integration").next_to(center_node, DOWN, buff=1)
        self.play(Write(label), run_time=1)
        self.wait(2)
        self.play(FadeOut(center_node), FadeOut(label), run_time=0.5)

