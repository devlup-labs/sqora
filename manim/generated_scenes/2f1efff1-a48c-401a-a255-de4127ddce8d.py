from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title_1 = Text("Newton's Third Law", font_size=40, color=YELLOW_C)
        title_1.to_edge(UP, buff=1)
        
        intro_text1 = Text("Welcome to SQORA. Let's master this law", font_size=28, width=config.frame_width - 2)
        intro_text2 = Text("for your JEE/NEET preparation.", font_size=28, width=config.frame_width - 2)
        
        intro_group = VGroup(intro_text1, intro_text2).arrange(DOWN, buff=0.5).next_to(title_1, DOWN, buff=1)
        
        self.play(Write(title_1))
        self.play(FadeIn(intro_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: The Definition ---
        title_2 = Text("The Definition", font_size=40, color=YELLOW_C)
        title_2.to_edge(UP, buff=1)
        
        def_text1 = Text("To every action, there is always an", font_size=28, width=config.frame_width - 2)
        def_text2 = Text("equal and opposite reaction.", font_size=28, width=config.frame_width - 2, color=BLUE_C)
        def_text3 = Text("Forces always exist in pairs.", font_size=28, width=config.frame_width - 2)
        
        def_group = VGroup(def_text1, def_text2, def_text3).arrange(DOWN, buff=0.5).next_to(title_2, DOWN, buff=1)
        
        self.play(Write(title_2))
        self.play(FadeIn(def_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Three Golden Rules ---
        title_3 = Text("Three Golden Rules", font_size=40, color=YELLOW_C)
        title_3.to_edge(UP, buff=0.5)
        
        rule1 = Text("1. Different Bodies: Action and reaction act on different objects.", font_size=28, width=config.frame_width - 2)
        rule2 = Text("2. Simultaneous: There is no time lag between them.", font_size=28, width=config.frame_width - 2)
        rule3 = Text("3. Same Nature: Both forces must be of the same type.", font_size=28, width=config.frame_width - 2)
        
        rules_group = VGroup(rule1, rule2, rule3).arrange(DOWN, buff=0.7).next_to(title_3, DOWN, buff=0.8)
        
        self.play(Write(title_3))
        for rule in rules_group:
            self.play(FadeIn(rule))
            self.wait(1)
        
        self.wait(1)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Mathematical Representation ---
        title_4 = Text("Mathematical Representation", font_size=40, color=YELLOW_C)
        title_4.to_edge(UP, buff=1)
        
        math_eq = MathTex(r"\vec{F}_{AB} = -\vec{F}_{BA}", font_size=60, color=GREEN_C)
        
        math_desc1 = Text("Force of A on B", font_size=28)
        math_desc2 = Text("is equal and opposite to", font_size=28)
        math_desc3 = Text("Force of B on A", font_size=28)
        
        math_group = VGroup(math_eq, math_desc1, math_desc2, math_desc3).arrange(DOWN, buff=0.5).next_to(title_4, DOWN, buff=0.8)
        
        self.play(Write(title_4))
        self.play(Create(math_eq))
        self.play(FadeIn(math_desc1), FadeIn(math_desc2), FadeIn(math_desc3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: Real-World Examples ---
        title_5 = Text("Real-World Examples", font_size=40, color=YELLOW_C)
        title_5.to_edge(UP, buff=1)
        
        ex1 = Text("Walking: Foot pushes ground back, ground pushes foot forward.", font_size=28, width=config.frame_width - 2)
        ex2 = Text("Recoil: Bullet moves forward, gun pushes the shooter back.", font_size=28, width=config.frame_width - 2)
        
        ex_group = VGroup(ex1, ex2).arrange(DOWN, buff=0.8).next_to(title_5, DOWN, buff=1)
        
        self.play(Write(title_5))
        self.play(FadeIn(ex1))
        self.wait(1)
        self.play(FadeIn(ex2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 6: Pro-Tip (FBD vs Equilibrium) ---
        title_6 = Text("JEE/NEET Pro-Tip", font_size=40, color=RED_C)
        title_6.to_edge(UP, buff=0.5)
        
        tip1 = Text("Equilibrium: Two forces act on the SAME object.", font_size=28, width=config.frame_width - 2)
        tip2 = Text("Third Law: Two forces act on DIFFERENT objects.", font_size=28, width=config.frame_width - 2)
        tip3 = Text("Example: Weight and Normal force are NOT a pair!", font_size=28, width=config.frame_width - 2, color=YELLOW_C)
        
        tip_group = VGroup(tip1, tip2, tip3).arrange(DOWN, buff=0.7).next_to(title_6, DOWN, buff=0.8)
        
        self.play(Write(title_6))
        self.play(FadeIn(tip1))
        self.play(FadeIn(tip2))
        self.wait(1)
        self.play(FadeIn(tip3))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

        # --- Section 7: Conclusion ---
        final_text = Text("Master these concepts for your exams!", font_size=40, color=BLUE_C)
        logo_text = Text("SQORA", font_size=50, color=YELLOW_C).next_to(final_text, DOWN, buff=1)
        
        self.play(Write(final_text))
        self.play(FadeIn(logo_text))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))