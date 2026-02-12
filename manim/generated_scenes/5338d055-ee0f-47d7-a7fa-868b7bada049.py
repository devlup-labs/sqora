from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title1 = Text("Einstein's Famous Equation", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        intro1 = Text("Proposed by Albert Einstein in 1905.", font_size=28, width=config.frame_width - 2)
        intro2 = Text("It changed how we understand the universe.", font_size=28, width=config.frame_width - 2)
        intro3 = Text("Crucial for JEE/NEET: Atoms and Nuclei chapter.", font_size=28, width=config.frame_width - 2)
        
        v1 = VGroup(title1, intro1, intro2, intro3).arrange(DOWN, buff=0.5).to_edge(UP, buff=1)
        
        self.play(Write(title1))
        self.wait(1)
        self.play(FadeIn(intro1))
        self.play(FadeIn(intro2))
        self.play(FadeIn(intro3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: The Equation ---
        title2 = Text("What do the letters mean?", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        eq1 = MathTex("E = mc^2", font_size=60, color=BLUE_C).shift(UP * 0.5)
        
        def_e = Text("E: Total energy contained within an object", font_size=28, width=config.frame_width - 2)
        def_m = Text("m: Mass of the object", font_size=28, width=config.frame_width - 2)
        def_c = Text("c: Speed of light (approx. 3 x 10^8 m/s)", font_size=28, width=config.frame_width - 2)
        
        defs = VGroup(def_e, def_m, def_c).arrange(DOWN, buff=0.3).next_to(eq1, DOWN, buff=0.8)
        
        self.play(Write(title2.to_edge(UP)))
        self.play(Write(eq1))
        self.wait(1)
        for d in defs:
            self.play(FadeIn(d))
            self.wait(0.5)
        
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Mass Defect & Binding Energy ---
        title3 = Text("Mass Defect & Binding Energy", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        md_text = Text("Mass Defect (Δm): Missing mass when a nucleus forms.", font_size=28, width=config.frame_width - 2)
        be_text = Text("This mass converts into Binding Energy (BE).", font_size=28, width=config.frame_width - 2)
        be_formula = MathTex("BE = \\Delta m \\times c^2", font_size=44, color=GREEN_C)
        
        v3 = VGroup(title3, md_text, be_text, be_formula).arrange(DOWN, buff=0.5).to_edge(UP, buff=1)
        
        self.play(Write(title3))
        self.play(FadeIn(md_text))
        self.play(FadeIn(be_text))
        self.play(Write(be_formula))
        self.wait(2)
        
        shortcut_box = SurroundingRectangle(be_formula, color=RED_C)
        shortcut_text = Text("JEE/NEET Shortcut: 1 amu ≈ 931.5 MeV", font_size=32, color=RED_C, width=config.frame_width - 2)
        shortcut_text.next_to(shortcut_box, DOWN, buff=0.5)
        
        self.play(Create(shortcut_box), Write(shortcut_text))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Example ---
        title4 = Text("The Power of 1 Gram", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        ex_text = Text("Converting 1 paperclip (1g) entirely into energy:", font_size=28, width=config.frame_width - 2)
        calc1 = MathTex("E = (0.001\\text{ kg}) \\times (3 \\times 10^8\\text{ m/s})^2", font_size=36)
        calc2 = MathTex("E = 9 \\times 10^{13}\\text{ Joules}", font_size=40, color=BLUE_C)
        fact = Text("Enough to power a city for an entire day!", font_size=28, color=GREY_A, width=config.frame_width - 2)
        
        v4 = VGroup(title4, ex_text, calc1, calc2, fact).arrange(DOWN, buff=0.5).to_edge(UP, buff=1)
        
        self.play(Write(title4))
        self.play(FadeIn(ex_text))
        self.play(Write(calc1))
        self.wait(1)
        self.play(ReplacementTransform(calc1.copy(), calc2))
        self.play(FadeIn(fact))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: Summary ---
        summary_title = Text("Summary for your Notes", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        s1 = Text("1. Mass and Energy are interconvertible.", font_size=28, width=config.frame_width - 2)
        s2 = Text("2. Use 1 amu = 931.5 MeV for quick calculations.", font_size=28, width=config.frame_width - 2)
        s3 = Text("3. Energy is released when mass is 'lost'.", font_size=28, width=config.frame_width - 2)
        
        v5 = VGroup(summary_title, s1, s2, s3).arrange(DOWN, buff=0.6).to_edge(UP, buff=1)
        
        self.play(Write(summary_title))
        self.play(FadeIn(s1))
        self.play(FadeIn(s2))
        self.play(FadeIn(s3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))