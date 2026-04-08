from manim import *
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tokens import *

class GeneratedScene(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        
        core = Circle(radius=1, color=PRIMARY_COLOR, fill_opacity=0.8)
        glow = Circle(radius=1.2, color=PRIMARY_COLOR, fill_opacity=0.2)
        
        nodes = VGroup(*[Dot(point=[2*np.cos(a), 2*np.sin(a), 0], color=TEXT_COLOR) for a in np.linspace(0, 2*PI, 8, endpoint=False)])
        connections = VGroup(*[Line(core.get_center(), node.get_center(), stroke_width=2, color=GREY_B) for node in nodes])
        
        brain = VGroup(core, glow, nodes, connections)
        text = get_title("Artificial Intelligence")
        
        self.play(Create(core), FadeIn(glow), run_time=1)
        self.play(Create(connections), FadeIn(nodes), run_time=1)
        self.play(Write(text.to_edge(UP)), run_time=1)
        
        # Pulsing
        self.play(glow.animate.scale(1.5), core.animate.scale(1.1), rate_func=there_and_back, run_time=2)
        self.wait(1)
        self.play(FadeOut(brain), FadeOut(text), run_time=0.5)

