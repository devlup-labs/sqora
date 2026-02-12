from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title = Text("Newton's Laws of Motion (NLM)", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        subtitle = Text("A JEE/NEET Perspective", font_size=28, color=WHITE, width=config.frame_width - 2)
        intro_group = VGroup(title, subtitle).arrange(DOWN, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(subtitle))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: First Law ---
        title1 = Text("1. Newton's First Law (Inertia)", font_size=40, color=BLUE_C, width=config.frame_width - 2)
        p1a = Text("Every object continues in its state of rest or uniform motion", font_size=28, width=config.frame_width - 2)
        p1b = Text("unless an external Net Force acts on it.", font_size=28, width=config.frame_width - 2)
        
        frame_info1 = Text("Inertial Frame: Rest or constant velocity.", font_size=28, color=GREY_A, width=config.frame_width - 2)
        frame_info2 = Text("Non-Inertial Frame: Accelerating (Use Pseudo Force).", font_size=28, color=GREY_A, width=config.frame_width - 2)
        
        v1 = VGroup(title1, p1a, p1b, frame_info1, frame_info2).arrange(DOWN, buff=0.4).to_edge(UP)
        
        self.play(Write(title1))
        self.play(FadeIn(p1a), FadeIn(p1b))
        self.wait(1)
        self.play(FadeIn(frame_info1))
        self.play(FadeIn(frame_info2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Second Law ---
        title2 = Text("2. Newton's Second Law", font_size=40, color=GREEN_C, width=config.frame_width - 2)
        eq1 = MathTex(r"\vec{F}_{net} = \frac{d\vec{p}}{dt}", font_size=36)
        eq2 = MathTex(r"\vec{F} = m\vec{a} \text{ (if mass is constant)}", font_size=36)
        
        var_mass1 = Text("Variable Mass (e.g., Rockets):", font_size=28, color=WHITE, width=config.frame_width - 2)
        var_mass2 = MathTex(r"F = v \frac{dm}{dt}", font_size=36, color=YELLOW_C)
        
        v2 = VGroup(title2, eq1, eq2, var_mass1, var_mass2).arrange(DOWN, buff=0.4)
        
        self.play(Write(title2))
        self.play(Write(eq1))
        self.wait(1)
        self.play(ReplacementTransform(eq1.copy(), eq2))
        self.play(FadeIn(var_mass1))
        self.play(Write(var_mass2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Third Law ---
        title3 = Text("3. Newton's Third Law", font_size=40, color=RED_C, width=config.frame_width - 2)
        p3a = Text("To every action, there is an equal and opposite reaction.", font_size=28, width=config.frame_width - 2)
        p3b = Text("CRITICAL: They act on DIFFERENT bodies.", font_size=28, color=YELLOW_C, width=config.frame_width - 2)
        
        eq3 = MathTex(r"\vec{F}_{AB} = -\vec{F}_{BA}", font_size=36)
        
        v3 = VGroup(title3, p3a, p3b, eq3).arrange(DOWN, buff=0.5)
        
        self.play(Write(title3))
        self.play(FadeIn(p3a))
        self.play(FadeIn(p3b))
        self.play(Write(eq3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: Problem Solving ---
        title4 = Text("Solving NLM Problems", font_size=40, color=WHITE, width=config.frame_width - 2)
        step1 = Text("1. Identify the System (the object of interest).", font_size=28, width=config.frame_width - 2)
        step2 = Text("2. Draw FBD: Represent object as a dot with all forces.", font_size=28, width=config.frame_width - 2)
        step3 = Text("3. Choose Axes and apply sum of F = ma.", font_size=28, width=config.frame_width - 2)
        
        v4 = VGroup(title4, step1, step2, step3).arrange(DOWN, buff=0.5)
        
        self.play(Write(title4))
        self.play(FadeIn(step1))
        self.play(FadeIn(step2))
        self.play(FadeIn(step3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 6: Quick Quiz ---
        quiz_title = Text("Quick Quiz", font_size=40, color=YELLOW_C, width=config.frame_width - 2)
        quiz_q1 = Text("A book is resting on a table.", font_size=28, width=config.frame_width - 2)
        quiz_q2 = Text("Are Weight and Normal force an Action-Reaction pair?", font_size=28, color=WHITE, width=config.frame_width - 2)
        
        v5 = VGroup(quiz_title, quiz_q1, quiz_q2).arrange(DOWN, buff=0.5)
        
        self.play(Write(quiz_title))
        self.play(FadeIn(quiz_q1))
        self.play(FadeIn(quiz_q2))
        self.wait(3)
        self.play(FadeOut(*self.mobjects))

        # Final Message
        final_text = Text("Master the FBD to master NLM!", font_size=40, color=GREEN_C, width=config.frame_width - 2)
        self.play(Write(final_text))
        self.wait(2)
        self.play(FadeOut(final_text))

# End of script