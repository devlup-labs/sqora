from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title = Text("Vector Calculus: Gradient and Curl", font_size=40, color=BLUE_C)
        title.to_edge(UP)
        
        del_op_text = Text("The Del Operator is the foundation:", font_size=28, width=config.frame_width - 2)
        del_op_math = MathTex(
            "\\nabla = \\hat{i} \\frac{\\partial}{\\partial x} + \\hat{j} \\frac{\\partial}{\\partial y} + \\hat{k} \\frac{\\partial}{\\partial z}",
            font_size=36, color=YELLOW_C
        )
        
        group1 = VGroup(title, del_op_text, del_op_math).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(del_op_text))
        self.play(Write(del_op_math))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: Gradient ---
        grad_title = Text("Properties of Gradient", font_size=40, color=GREEN_C)
        grad_title.to_edge(UP)
        
        grad_def = Text("Gradient acts on a scalar field to produce a vector field.", font_size=28, width=config.frame_width - 2)
        grad_math = MathTex(
            "\\nabla \\phi = \\frac{\\partial \\phi}{\\partial x} \\hat{i} + \\frac{\\partial \\phi}{\\partial y} \\hat{j} + \\frac{\\partial \\phi}{\\partial z} \\hat{k}",
            font_size=36, color=WHITE
        )
        
        grad_prop = Text("It points in the direction of maximum rate of increase.", font_size=28, width=config.frame_width - 2)
        
        self.play(Write(grad_title))
        self.play(FadeIn(grad_def))
        self.wait(1)
        self.play(Write(grad_math))
        self.wait(1)
        self.play(FadeIn(grad_prop))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Curl ---
        curl_title = Text("Properties of Curl", font_size=40, color=RED_C)
        curl_title.to_edge(UP)
        
        curl_def = Text("Curl measures the rotation of a vector field.", font_size=28, width=config.frame_width - 2)
        curl_math = MathTex(
            "\\nabla \\times \\vec{A} = \\begin{vmatrix} \\hat{i} & \\hat{j} & \\hat{k} \\\\ \\frac{\\partial}{\\partial x} & \\frac{\\partial}{\\partial y} & \\frac{\\partial}{\\partial z} \\\\ A_x & A_y & A_z \\end{vmatrix}",
            font_size=36, color=WHITE
        )
        
        curl_prop = Text("If curl is zero, the field is called Irrotational.", font_size=28, width=config.frame_width - 2)
        
        self.play(Write(curl_title))
        self.play(FadeIn(curl_def))
        self.wait(1)
        self.play(Write(curl_math))
        self.wait(1)
        self.play(FadeIn(curl_prop))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Important Identities ---
        id_title = Text("Key Vector Identities", font_size=40, color=YELLOW_C)
        id_title.to_edge(UP)
        
        id1_text = Text("1. Curl of a Gradient is always zero:", font_size=28, width=config.frame_width - 2)
        id1_math = MathTex("\\nabla \\times (\\nabla \\phi) = 0", font_size=36, color=BLUE_C)
        
        id2_text = Text("2. Divergence of a Curl is always zero:", font_size=28, width=config.frame_width - 2)
        id2_math = MathTex("\\nabla \\cdot (\\nabla \\times \\vec{A}) = 0", font_size=36, color=GREEN_C)
        
        ids = VGroup(id1_text, id1_math, id2_text, id2_math).arrange(DOWN, buff=0.4)
        ids.next_to(id_title, DOWN, buff=0.5)
        
        self.play(Write(id_title))
        self.play(FadeIn(id1_text))
        self.play(Write(id1_math))
        self.wait(1)
        self.play(FadeIn(id2_text))
        self.play(Write(id2_math))
        self.wait(2)
        
        # Final Clear
        self.play(FadeOut(*self.mobjects))
        
        summary = Text("Master these for JEE/NEET Physics!", font_size=40, color=WHITE)
        self.play(Write(summary))
        self.wait(2)