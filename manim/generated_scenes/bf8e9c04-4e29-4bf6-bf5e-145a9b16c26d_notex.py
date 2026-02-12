from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title1 = Text("Electrostatic Force: F = qE", font_size=40, color=YELLOW_C)
        title1.to_edge(UP)
        
        intro_text = Text(
            "In JEE/NEET Physics, QE refers to the force acting on a charge.",
            font_size=28,
            width=config.frame_width - 2
        )
        
        formula_main = Text("F = qE", font_size=72, color=BLUE_C)
        
        self.play(Write(title1))
        self.play(FadeIn(intro_text, shift=DOWN))
        self.wait(1)
        self.play(Write(formula_main))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: Breakdown of Variables ---
        title2 = Text("The Breakdown", font_size=40, color=YELLOW_C).to_edge(UP)
        
        # Variable q
        q_sym = Text("q", color=GREEN_C)
        q_desc = Text("Charge (Measured in Coulombs)", font_size=28)
        q_desc.set_width(config.frame_width - 3)
        q_grp = VGroup(q_sym, q_desc).arrange(RIGHT, buff=0.5)
        
        # Variable E
        e_sym = Text("E", color=RED_C)
        e_desc = Text("Electric Field Intensity (N/C or V/m)", font_size=28)
        e_desc.set_width(config.frame_width - 3)
        e_grp = VGroup(e_sym, e_desc).arrange(RIGHT, buff=0.5)
        
        # Variable F
        f_sym = Text("F", color=BLUE_C)
        f_desc = Text("Force (Measured in Newtons)", font_size=28)
        f_desc.set_width(config.frame_width - 3)
        f_grp = VGroup(f_sym, f_desc).arrange(RIGHT, buff=0.5)
        
        vars_vgroup = VGroup(q_grp, e_grp, f_grp).arrange(DOWN, buff=0.6, aligned_edge=LEFT)
        vars_vgroup.shift(DOWN * 0.5)
        
        self.play(Write(title2))
        self.play(FadeIn(vars_vgroup))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Vector Nature ---
        title3 = Text("Direction is Key", font_size=40, color=YELLOW_C).to_edge(UP)
        
        pos_charge = Text(
            "Positive Charge (+q): Force is in the SAME direction as E",
            font_size=28,
            color=GREEN_C,
            width=config.frame_width - 2
        )
        
        neg_charge = Text(
            "Negative Charge (-q): Force is in the OPPOSITE direction to E",
            font_size=28,
            color=RED_C,
            width=config.frame_width - 2
        )
        
        dir_grp = VGroup(pos_charge, neg_charge).arrange(DOWN, buff=1)
        
        self.play(Write(title3))
        self.play(FadeIn(pos_charge))
        self.wait(1)
        self.play(FadeIn(neg_charge))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Mechanics Integration ---
        title4 = Text("JEE/NEET Application: Mechanics", font_size=40, color=YELLOW_C).to_edge(UP)
        
        mech_text = Text(
            "Combining Electrostatics with Newton's Second Law:",
            font_size=28,
            width=config.frame_width - 2
        )
        
        accel_eq = Text("qE = ma", font_size=48)
        accel_res = Text("a = \{qE}{m}", font_size=60, color=BLUE_C)
        
        mech_grp = VGroup(mech_text, accel_eq, accel_res).arrange(DOWN, buff=0.5)
        
        self.play(Write(title4))
        self.play(FadeIn(mech_text))
        self.play(Write(accel_eq))
        self.wait(1)
        self.play(ReplacementTransform(accel_eq.copy(), accel_res))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: Equilibrium & Work ---
        title5 = Text("Equilibrium and Work", font_size=40, color=YELLOW_C).to_edge(UP)
        
        eq_text = Text("For a hanging charge in a field:", font_size=28, width=config.frame_width - 2)
        eq_math = Text("T \\sin \\theta = qE", font_size=36)
        
        work_text = Text("Work done moving a charge:", font_size=28, width=config.frame_width - 2)
        work_math = Text("W = (qE) \· d", font_size=36)
        
        final_grp = VGroup(eq_text, eq_math, work_text, work_math).arrange(DOWN, buff=0.4)
        
        self.play(Write(title5))
        self.play(FadeIn(eq_text), Write(eq_math))
        self.wait(1)
        self.play(FadeIn(work_text), Write(work_math))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 6: Alternative Meanings ---
        title6 = Text("Other Meanings of 'QE'", font_size=40, color=GREY_A).to_edge(UP)
        
        math_qe = Text(
            "1. Quadratic Equations (Math): ax^2 + bx + c = 0",
            font_size=28,
            width=config.frame_width - 2
        )
        
        phys_qe = Text(
            "2. Quantum Efficiency: Ratio of electrons to photons",
            font_size=28,
            width=config.frame_width - 2
        )
        
        alt_grp = VGroup(math_qe, phys_qe).arrange(DOWN, buff=0.8)
        
        self.play(Write(title6))
        self.play(FadeIn(alt_grp))
        self.wait(2)
        
        # Final Outro
        self.play(FadeOut(alt_grp), FadeOut(title6))
        final_msg = Text("Master F = qE for your Physics exams!", font_size=40, color=YELLOW_C)
        final_msg.set_width(config.frame_width - 2)
        self.play(Write(final_msg))
        self.wait(2)
