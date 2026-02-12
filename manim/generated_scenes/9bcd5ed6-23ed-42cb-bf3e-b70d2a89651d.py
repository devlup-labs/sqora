from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- SECTION 1: GRADIENT INTRODUCTION ---
        title1 = Text("Properties of Gradient", font_size=40, color=BLUE_C)
        title1.to_edge(UP)
        
        desc1 = Text("The gradient of a scalar field is a vector field.", font_size=28)
        desc1.set_width(config.frame_width - 2)
        
        math1 = MathTex(
            "\\nabla \\phi = \\frac{\\partial \\phi}{\\partial x} \\hat{i} + \\frac{\\partial \\phi}{\\partial y} \\hat{j} + \\frac{\\partial \\phi}{\\partial z} \\hat{k}",
            font_size=36, color=YELLOW_C
        )
        
        self.play(Write(title1))
        self.play(FadeIn(desc1, shift=DOWN))
        self.wait(1)
        self.play(Write(math1.next_to(desc1, DOWN, buff=0.5)))
        self.wait(2)
        
        self.play(FadeOut(*self.mobjects))

        # --- SECTION 2: GRADIENT PROPERTIES ---
        title2 = Text("Key Properties of Gradient", font_size=40, color=BLUE_C)
        title2.to_edge(UP)

        prop1 = Text("1. It points in the direction of maximum increase.", font_size=28)
        prop1.set_width(config.frame_width - 2)
        
        prop2 = Text("2. It is always perpendicular to the level surface.", font_size=28)
        prop2.set_width(config.frame_width - 2)

        props_vgroup = VGroup(prop1, prop2).arrange(DOWN, buff=0.5).next_to(title2, DOWN, buff=1)

        self.play(Write(title2))
        self.play(FadeIn(prop1))
        self.wait(1)
        self.play(FadeIn(prop2))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))

        # --- SECTION 3: CURL INTRODUCTION ---
        title3 = Text("Properties of Curl", font_size=40, color=GREEN_C)
        title3.to_edge(UP)

        desc3 = Text("Curl measures the rotation of a vector field.", font_size=28)
        desc3.set_width(config.frame_width - 2)

        math3 = MathTex(
            "\\nabla \\times \\vec{V} = \\begin{vmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ \\frac{\\partial}{\\partial x} & \\frac{\\partial}{\\partial y} & \\frac{\\partial}{\\partial z} \\\\ V_x & V_y & V_z \\end{vmatrix}",
            font_size=36, color=YELLOW_C
        )

        self.play(Write(title3))
        self.play(FadeIn(desc3.next_to(title3, DOWN, buff=0.5)))
        self.wait(1)
        self.play(Write(math3.next_to(desc3, DOWN, buff=0.5)))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))

        # --- SECTION 4: CURL PROPERTIES ---
        title4 = Text("Key Properties of Curl", font_size=40, color=GREEN_C)
        title4.to_edge(UP)

        prop3 = Text("1. If curl is zero, the field is Irrotational.", font_size=28)
        prop3.set_width(config.frame_width - 2)

        math4 = MathTex("\\nabla \\times \\vec{V} = 0", font_size=36, color=RED_C)

        prop4 = Text("2. The curl of any gradient is always zero.", font_size=28)
        prop4.set_width(config.frame_width - 2)

        math5 = MathTex("\\nabla \\times (\\nabla \\phi) = 0", font_size=36, color=YELLOW_C)

        content = VGroup(prop3, math4, prop4, math5).arrange(DOWN, buff=0.4).next_to(title4, DOWN, buff=0.5)

        self.play(Write(title4))
        self.play(FadeIn(prop3))
        self.play(Write(math4))
        self.wait(1)
        self.play(FadeIn(prop4))
        self.play(Write(math5))
        self.wait(2)

        self.play(FadeOut(*self.mobjects))

        # --- SECTION 5: SUMMARY ---
        summary_title = Text("Summary", font_size=40, color=WHITE)
        summary_title.to_edge(UP)

        sum1 = Text("Gradient: Scalar to Vector (Max Increase)", font_size=28, color=BLUE_C)
        sum1.set_width(config.frame_width - 2)
        
        sum2 = Text("Curl: Vector to Vector (Rotation)", font_size=28, color=GREEN_C)
        sum2.set_width(config.frame_width - 2)

        summary_group = VGroup(sum1, sum2).arrange(DOWN, buff=0.8).center()

        self.play(Write(summary_title))
        self.play(FadeIn(summary_group))
        self.wait(3)

        self.play(FadeOut(*self.mobjects))