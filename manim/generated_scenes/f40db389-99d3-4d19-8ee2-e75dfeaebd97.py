from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # Section 1: Introduction
        title1 = Text("Angular Momentum (L)", font_size=40, color=YELLOW_C)
        title1.to_edge(UP)
        
        intro_text1 = Text(
            "Angular Momentum is the 'quantity of rotation' an object has.",
            font_size=28, width=config.frame_width - 2
        )
        intro_text2 = Text(
            "It is the rotational equivalent of linear momentum (p = mv).",
            font_size=28, width=config.frame_width - 2
        )
        
        intro_group = VGroup(intro_text1, intro_text2).arrange(DOWN, buff=0.5).next_to(title1, DOWN, buff=1)
        
        self.play(Write(title1))
        self.play(FadeIn(intro_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Section 2: Point Mass
        title2 = Text("For a Point Mass", font_size=40, color=BLUE_C)
        title2.to_edge(UP)
        
        point_text = Text(
            "For a particle of mass m moving with velocity v at distance r:",
            font_size=28, width=config.frame_width - 2
        )
        
        eq_point1 = MathTex(r"\vec{L} = \vec{r} \times \vec{p} = m(\vec{r} \times \vec{v})", font_size=36)
        eq_point2 = MathTex(r"L = mvr \sin \theta", font_size=36)
        
        point_group = VGroup(point_text, eq_point1, eq_point2).arrange(DOWN, buff=0.6).next_to(title2, DOWN, buff=0.8)
        
        self.play(Write(title2))
        self.play(FadeIn(point_text))
        self.play(Write(eq_point1))
        self.play(Write(eq_point2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Section 3: Rigid Body
        title3 = Text("For a Rotating Rigid Body", font_size=40, color=GREEN_C)
        title3.to_edge(UP)
        
        rigid_text = Text(
            "We swap mass for Moment of Inertia (I) and velocity for Angular Velocity.",
            font_size=28, width=config.frame_width - 2
        )
        
        eq_rigid = MathTex(r"L = I \omega", font_size=40)
        
        unit_label = Text("Units:", font_size=28, color=GREY_A)
        unit_val = Text("kg m^2 / s", font_size=28)
        unit_group = VGroup(unit_label, unit_val).arrange(RIGHT, buff=0.3)
        
        rigid_content = VGroup(rigid_text, eq_rigid, unit_group).arrange(DOWN, buff=0.7).next_to(title3, DOWN, buff=0.8)
        
        self.play(Write(title3))
        self.play(FadeIn(rigid_text))
        self.play(Write(eq_rigid))
        self.play(FadeIn(unit_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Section 4: Conservation Law
        title4 = Text("Conservation of Angular Momentum", font_size=40, color=RED_C)
        title4.to_edge(UP)
        
        cons_text = Text(
            "If the net external Torque is zero, total angular momentum is constant.",
            font_size=28, width=config.frame_width - 2
        )
        
        eq_cons1 = MathTex(r"\tau = 0 \implies L_1 = L_2", font_size=36)
        eq_cons2 = MathTex(r"I_1 \omega_1 = I_2 \omega_2", font_size=36)
        
        cons_group = VGroup(cons_text, eq_cons1, eq_cons2).arrange(DOWN, buff=0.6).next_to(title4, DOWN, buff=0.8)
        
        self.play(Write(title4))
        self.play(FadeIn(cons_text))
        self.play(Write(eq_cons1))
        self.play(Write(eq_cons2))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Section 5: Ice Skater Example
        title5 = Text("The Ice Skater Example", font_size=40, color=YELLOW_C)
        title5.to_edge(UP)
        
        skater_text1 = Text(
            "When a skater pulls her arms in, her Moment of Inertia (I) decreases.",
            font_size=28, width=config.frame_width - 2
        )
        skater_text2 = Text(
            "To keep L constant, her Angular Velocity must increase.",
            font_size=28, width=config.frame_width - 2
        )
        skater_text3 = Text(
            "Result: She spins much faster!",
            font_size=28, color=GREEN_C, width=config.frame_width - 2
        )
        
        skater_group = VGroup(skater_text1, skater_text2, skater_text3).arrange(DOWN, buff=0.5).next_to(title5, DOWN, buff=0.8)
        
        self.play(Write(title5))
        for line in skater_group:
            self.play(FadeIn(line))
            self.wait(1)
        self.wait(1)
        self.play(FadeOut(*self.mobjects))

        # Section 6: Bohr's Model
        title6 = Text("Bohr's Model of the Atom", font_size=40, color=BLUE_C)
        title6.to_edge(UP)
        
        bohr_text = Text(
            "Electrons revolve in orbits where angular momentum is quantized:",
            font_size=28, width=config.frame_width - 2
        )
        
        eq_bohr = MathTex(r"L = \frac{nh}{2\pi}", font_size=40)
        
        bohr_group = VGroup(bohr_text, eq_bohr).arrange(DOWN, buff=0.8).next_to(title6, DOWN, buff=1)
        
        self.play(Write(title6))
        self.play(FadeIn(bohr_text))
        self.play(Write(eq_bohr))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Section 7: Quick Comparison
        title7 = Text("Linear vs Rotational Motion", font_size=40, color=WHITE)
        title7.to_edge(UP)
        
        comp1 = Text("Mass (m)  --->  Inertia (I)", font_size=28, width=config.frame_width - 2)
        comp2 = Text("Velocity (v)  --->  Angular Velocity (omega)", font_size=28, width=config.frame_width - 2)
        comp3 = Text("Momentum (p)  --->  Angular Momentum (L)", font_size=28, width=config.frame_width - 2)
        comp4 = Text("Force (F)  --->  Torque (tau)", font_size=28, width=config.frame_width - 2)
        
        comp_group = VGroup(comp1, comp2, comp3, comp4).arrange(DOWN, buff=0.4).next_to(title7, DOWN, buff=0.8)
        
        self.play(Write(title7))
        self.play(FadeIn(comp_group))
        self.wait(2)
        self.play(FadeOut(*self.mobjects))

        # Final Thought
        final_text = Text(
            "Why does a diver tuck their body into a ball while jumping?",
            font_size=28, color=YELLOW_C, width=config.frame_width - 2
        )
        hint_text = Text(
            "Hint: Think about what happens to I and omega!",
            font_size=28, width=config.frame_width - 2
        )
        
        final_group = VGroup(final_text, hint_text).arrange(DOWN, buff=0.5).center()
        
        self.play(FadeIn(final_group))
        self.wait(3)
        self.play(FadeOut(final_group))

        # End of Scene
        thanks = Text("Keep Practicing for JEE/NEET!", font_size=40, color=GREEN_C)
        self.play(Write(thanks))
        self.wait(2)
        self.play(FadeOut(thanks))
```