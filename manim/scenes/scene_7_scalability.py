from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        root = Dot(color=PRIMARY_COLOR).scale(2)
        branches = VGroup()
        for i in range(3):
            branch = Line(root.get_center(), [i-1, 2, 0], color=GREY_B)
            leaf = Dot(point=[i-1, 2, 0], color=SECONDARY_COLOR)
            branches.add(VGroup(branch, leaf))
            
        text = get_title("Infinite Scalability")
        
        self.play(FadeIn(root), Write(text.to_edge(DOWN)), run_time=1)
        self.play(Create(branches), run_time=1.5)
        
        # Exponential growth effect
        more_branches = VGroup()
        for b in branches:
            for j in range(2):
                end = b[1].get_center() + [j-0.5, 1.5, 0]
                line = Line(b[1].get_center(), end, color=GREY_C)
                dot = Dot(point=end, color=ACCENT_COLOR)
                more_branches.add(VGroup(line, dot))
                
        self.play(Create(more_branches), run_time=1.5)
        self.wait(2)
        self.play(FadeOut(VGroup(root, branches, more_branches, text)), run_time=0.5)

