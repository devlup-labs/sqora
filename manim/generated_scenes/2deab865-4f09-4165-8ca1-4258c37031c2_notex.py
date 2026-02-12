from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title1 = Text("Wave Optics: Diffraction", font_size=40, color=YELLOW_C)
        title1.to_edge(UP)
        
        intro_text1 = Text(
            "Diffraction is the bending of waves around the corners",
            font_size=28, width=config.frame_width - 2
        )
        intro_text2 = Text(
            "of an obstacle or an opening into the shadow region.",
            font_size=28, width=config.frame_width - 2
        )
        
        intro_group = VGroup(intro_text1, intro_text2).arrange(DOWN, buff=0.4).next_to(title1, DOWN, buff=1)
        
        self.play(Write(title1))
        self.play(FadeIn(intro_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: The Golden Condition ---
        title2 = Text("The Golden Condition", font_size=40, color=YELLOW_C)
        title2.to_edge(UP)
        
        cond_text1 = Text(
            "For diffraction to be noticeable, the slit size (a)",
            font_size=28, width=config.frame_width - 2
        )
        cond_text2 = Text(
            "must be comparable to the wavelength of light.",
            font_size=28, width=config.frame_width - 2
        )
        
        condition_math = Text("a \\approx \\lambda", font_size=48, color=BLUE_C)
        
        cond_group = VGroup(cond_text1, cond_text2, condition_math).arrange(DOWN, buff=0.5).next_to(title2, DOWN, buff=1)
        
        self.play(Write(title2))
        self.play(FadeIn(cond_text1), FadeIn(cond_text2))
        self.play(Write(condition_math))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Single Slit Diffraction ---
        title3 = Text("Single Slit Diffraction", font_size=40, color=YELLOW_C)
        title3.to_edge(UP)
        
        slit_text = Text(
            "Condition for Minima (Dark Fringes):",
            font_size=28, width=config.frame_width - 2
        )
        
        minima_math = Text("a \\sin \\theta = n \\lambda", font_size=44, color=RED_C)
        
        n_val = Text(
            "where n = 1, 2, 3...",
            font_size=28, width=config.frame_width - 2
        )
        
        slit_group = VGroup(slit_text, minima_math, n_val).arrange(DOWN, buff=0.5).next_to(title3, DOWN, buff=1)
        
        self.play(Write(title3))
        self.play(FadeIn(slit_text))
        self.play(Write(minima_math))
        self.play(FadeIn(n_val))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Types of Diffraction ---
        title4 = Text("Types of Diffraction", font_size=40, color=YELLOW_C)
        title4.to_edge(UP)
        
        type1_title = Text("1. Fresnel Diffraction", font_size=32, color=GREEN_C)
        type1_desc = Text("Source and screen are at a finite distance.", font_size=28, width=config.frame_width - 2)
        
        type2_title = Text("2. Fraunhofer Diffraction", font_size=32, color=GREEN_C)
        type2_desc = Text("Source and screen are at infinite distance.", font_size=28, width=config.frame_width - 2)
        
        types_group = VGroup(type1_title, type1_desc, type2_title, type2_desc).arrange(DOWN, buff=0.4).next_to(title4, DOWN, buff=0.8)
        
        self.play(Write(title4))
        self.play(FadeIn(type1_title), FadeIn(type1_desc))
        self.wait(1)
        self.play(FadeIn(type2_title), FadeIn(type2_desc))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: Interference vs Diffraction ---
        title5 = Text("Interference vs. Diffraction", font_size=40, color=YELLOW_C)
        title5.to_edge(UP)
        
        diff1 = Text("Interference: Superposition from two wavefronts.", font_size=28, width=config.frame_width - 2)
        diff2 = Text("Diffraction: Superposition from one wavefront.", font_size=28, width=config.frame_width - 2)
        
        diff_group = VGroup(diff1, diff2).arrange(DOWN, buff=0.6).next_to(title5, DOWN, buff=1)
        
        self.play(Write(title5))
        self.play(FadeIn(diff1))
        self.play(FadeIn(diff2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 6: Central Maximum Formula ---
        title6 = Text("Width of Central Maximum", font_size=40, color=YELLOW_C)
        title6.to_edge(UP)
        
        formula_text = Text("The linear width (W) is given by:", font_size=28, width=config.frame_width - 2)
        
        final_formula = Text("W = \{2 \\lambda D}{a}", font_size=48, color=BLUE_C)
        
        label_text = Text("D = Screen Distance, a = Slit Width", font_size=24, color=GREY_A)
        
        final_group = VGroup(formula_text, final_formula, label_text).arrange(DOWN, buff=0.6).next_to(title6, DOWN, buff=1)
        
        self.play(Write(title6))
        self.play(FadeIn(formula_text))
        self.play(Write(final_formula))
        self.play(FadeIn(label_text))
        self.wait(3)
        
        # Final Clear
        self.play(FadeOut(*self.mobjects))

[instruction]The provided code is a Manim Community Edition (v0.19) script that creates an educational animation about Diffraction for JEE/NEET preparation. It covers the definition, the "Golden Condition", single-slit formulas, types of diffraction, and the comparison with interference, all while adhering to the strict formatting and LaTeX rules provided.