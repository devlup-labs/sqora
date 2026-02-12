from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title1 = Text("Potential Energy (PE)", font_size=40, color=YELLOW_C)
        title1.to_edge(UP)
        
        intro1 = Text("Potential Energy is often called 'Stored Energy'.", font_size=28, width=config.frame_width - 2)
        intro2 = Text("It is the energy an object has because of its position.", font_size=28, width=config.frame_width - 2)
        intro3 = Text("Think of it like a bank account ready to be spent!", font_size=28, width=config.frame_width - 2)
        
        intro_group = VGroup(intro1, intro2, intro3).arrange(DOWN, buff=0.5).next_to(title1, DOWN, buff=1)
        
        self.play(Write(title1))
        self.play(FadeIn(intro1))
        self.wait(1)
        self.play(FadeIn(intro2))
        self.wait(1)
        self.play(FadeIn(intro3))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 2: Gravitational Potential Energy ---
        title2 = Text("Gravitational Potential Energy", font_size=40, color=BLUE_C)
        title2.to_edge(UP)
        
        gpe_desc = Text("Energy due to height above the ground.", font_size=28, width=config.frame_width - 2)
        gpe_formula = MathTex("U = mgh", font_size=48, color=YELLOW_C)
        
        m_label = Text("m: Mass (kg)", font_size=28)
        g_label = Text("g: Gravity (9.8 or 10 m/s^2)", font_size=28)
        h_label = Text("h: Height (m)", font_size=28)
        
        labels = VGroup(m_label, g_label, h_label).arrange(DOWN, aligned_edge=LEFT).next_to(gpe_formula, DOWN, buff=0.5)
        
        self.play(Write(title2))
        self.play(FadeIn(gpe_desc.next_to(title2, DOWN)))
        self.play(Write(gpe_formula.shift(UP*0.5)))
        self.play(FadeIn(labels))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 3: Reference Level ---
        title3 = Text("The Reference Level", font_size=40, color=GREEN_C)
        title3.to_edge(UP)
        
        ref1 = Text("Potential energy is relative to a chosen point.", font_size=28, width=config.frame_width - 2)
        ref2 = Text("In exams, always decide your 'Zero Level' first!", font_size=28, width=config.frame_width - 2, color=RED_C)
        
        ref_group = VGroup(ref1, ref2).arrange(DOWN, buff=0.5).next_to(title3, DOWN, buff=1)
        
        self.play(Write(title3))
        self.play(FadeIn(ref1))
        self.wait(1)
        self.play(FadeIn(ref2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 4: Elastic Potential Energy ---
        title4 = Text("Elastic Potential Energy (Springs)", font_size=40, color=YELLOW_C)
        title4.to_edge(UP)
        
        spring_desc = Text("Work stored when stretching or compressing a spring.", font_size=28, width=config.frame_width - 2)
        spring_formula = MathTex("U = \\frac{1}{2} k x^2", font_size=48, color=BLUE_C)
        
        k_label = Text("k: Spring constant (stiffness)", font_size=28)
        x_label = Text("x: Displacement from natural position", font_size=28)
        
        spring_labels = VGroup(k_label, x_label).arrange(DOWN, aligned_edge=LEFT).next_to(spring_formula, DOWN, buff=0.5)
        
        self.play(Write(title4))
        self.play(FadeIn(spring_desc.next_to(title4, DOWN)))
        self.play(Write(spring_formula.shift(UP*0.5)))
        self.play(FadeIn(spring_labels))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 5: JEE/NEET Pro Perspective ---
        title5 = Text("Force and Potential Energy", font_size=40, color=RED_C)
        title5.to_edge(UP)
        
        pro1 = Text("PE is only defined for Conservative Forces.", font_size=28, width=config.frame_width - 2)
        pro2 = Text("Example: Gravity, Spring. (NOT Friction)", font_size=28, width=config.frame_width - 2)
        
        force_eq = MathTex("F = -\\frac{dU}{dx}", font_size=48, color=YELLOW_C)
        force_desc = Text("The slope of U vs x graph tells you the Force!", font_size=28, width=config.frame_width - 2)
        
        pro_group = VGroup(pro1, pro2, force_eq, force_desc).arrange(DOWN, buff=0.5).next_to(title5, DOWN)
        
        self.play(Write(title5))
        self.play(FadeIn(pro1))
        self.play(FadeIn(pro2))
        self.wait(1)
        self.play(Write(force_eq))
        self.play(FadeIn(force_desc))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 6: Work-Energy Theorem ---
        title6 = Text("Work-Energy Theorem", font_size=40, color=BLUE_C)
        title6.to_edge(UP)
        
        work_desc = Text("Work by conservative force = negative change in PE", font_size=28, width=config.frame_width - 2)
        work_eq1 = MathTex("W_c = -\\Delta U", font_size=48)
        work_eq2 = MathTex("W_c = -(U_f - U_i)", font_size=48)
        
        work_group = VGroup(work_desc, work_eq1, work_eq2).arrange(DOWN, buff=0.5).next_to(title6, DOWN, buff=1)
        
        self.play(Write(title6))
        self.play(FadeIn(work_desc))
        self.play(Write(work_eq1))
        self.play(Write(work_eq2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Section 7: Quick Check ---
        title7 = Text("Quick Check", font_size=40, color=GREEN_C)
        title7.to_edge(UP)
        
        prob = Text("Lift 2kg brick to 5m height (g = 10 m/s^2)", font_size=28, width=config.frame_width - 2)
        calc1 = MathTex("U = mgh", font_size=40)
        calc2 = MathTex("U = 2 \\times 10 \\times 5", font_size=40)
        
        res_val = MathTex("U = 100", font_size=48, color=YELLOW_C)
        res_unit = Text("Joules", font_size=36, color=YELLOW_C)
        res_group = HGroup(res_val, res_unit).arrange(RIGHT, buff=0.2)
        
        check_group = VGroup(prob, calc1, calc2).arrange(DOWN, buff=0.5).next_to(title7, DOWN)
        
        self.play(Write(title7))
        self.play(FadeIn(prob))
        self.wait(1)
        self.play(Write(calc1))
        self.play(ReplacementTransform(calc1, calc2))
        self.wait(1)
        self.play(FadeIn(res_group.next_to(calc2, DOWN)))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # --- Final Screen ---
        final_text = Text("Master Potential Energy for JEE/NEET!", font_size=40, color=YELLOW_C)
        self.play(Write(final_text))
        self.wait(2)
        self.play(FadeOut(final_text))

class HGroup(VGroup):
    def __init__(self, *mobjects, **kwargs):
        VGroup.__init__(self, *mobjects, **kwargs)
        self.arrange(RIGHT)
<ctrl63>