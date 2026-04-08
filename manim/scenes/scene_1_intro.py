from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        logo = Circle(radius=1.5, color=PRIMARY_COLOR, fill_opacity=0.5)
        inner = Star(n=5, color=SECONDARY_COLOR, fill_opacity=1).scale(0.5)
        logo_group = VGroup(logo, inner)
        
        title = get_title("SQORA")
        subtitle = get_body("The Future of AI Content", color=GREY_A).scale(0.8)
        
        content = VGroup(logo_group, title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(FadeIn(logo_group, scale=0.5), run_time=1)
        self.play(logo_group.animate.rotate(PI/4), run_time=1)
        self.play(Write(title), run_time=1)
        self.play(FadeIn(subtitle, shift=UP*0.3), run_time=1)
        self.wait(2)
        self.play(FadeOut(content), run_time=0.5)

