from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Set background color
        self.camera.background_color = "#0a1224"

        # --- Section 1: Introduction ---
        title1 = Text("Newton's Third Law of Motion", font_size=40, color=YELLOW_C)
        title1.to_edge(UP, buff=0.5)
        
        def_line1 = Text("For every action, there is always an equal", 
                         font_size=28, width=config.frame_width - 2)
        def_line2 = Text("and opposite reaction.", 
                         font_size=28, width=config.frame_width - 2)
        
        definition = VGroup(def_line1, def_line2).arrange(DOWN, buff=0.3)
        
        self.play(Write(title1))
        self.play(FadeIn(definition))
        self.wait(2)
        self.play(FadeOut(title1), FadeOut(definition))

        # --- Section 2: Key Characteristics ---
        title2 = Text("Key Characteristics", font_size=40, color=BLUE_C)
        title2.to_edge(UP, buff=0.5)
        
        char1 = Text("1. Forces always occur in pairs.", 
                     font_size=28, width=config.frame_width - 2)
        char2 = Text("2. Action and Reaction act on DIFFERENT bodies.", 
                     font_size=28, width=config.frame_width - 2)
        char3 = Text("3. They are simultaneous (no time lag).", 
                     font_size=28, width=config.frame_width - 2)
        
        chars = VGroup(char1, char2, char3).arrange(DOWN, buff=0.6).next_to(title2, DOWN, buff=1)
        
        self.play(Write(title2))
        for char in chars:
            self.play(FadeIn(char, shift=RIGHT))
            self.wait(1)
        
        self.wait(1)
        self.play(FadeOut(title2), FadeOut(chars))

        # --- Section 3: Mathematical Representation ---
        title3 = Text("Mathematical Form", font_size=40, color=GREEN_C)
        title3.to_edge(UP, buff=0.5)
        
        equation = MathTex(r"\vec{F}_{AB} = -\vec{F}_{BA}", font_size=60)
        
        label_a = Text("Force on A by B", font_size=24, color=BLUE_C)
        label_b = Text("Force on B by A", font_size=24, color=RED_C)
        
        labels = VGroup(label_a, label_b).arrange(RIGHT, buff=2).next_to(equation, DOWN, buff=1)
        
        self.play(Write(title3))
        self.play(Write(equation))
        self.play(FadeIn(label_a), FadeIn(label_b))
        self.wait(2)
        self.play(FadeOut(title3), FadeOut(equation), FadeOut(labels))

        # --- Section 4: Visual Example ---
        title4 = Text("Interaction Example", font_size=40, color=WHITE)
        title4.to_edge(UP, buff=0.5)
        
        obj_a = Circle(radius=0.6, color=BLUE_C, fill_opacity=0.5).shift(LEFT * 1.5)
        obj_b = Circle(radius=0.6, color=RED_C, fill_opacity=0.5).shift(RIGHT * 1.5)
        
        text_a = Text("A", font_size=28).move_to(obj_a.get_center())
        text_b = Text("B", font_size=28).move_to(obj_b.get_center())
        
        arrow_to_left = Arrow(start=obj_b.get_left(), end=obj_a.get_right(), color=YELLOW_C, buff=0.1)
        arrow_to_right = Arrow(start=obj_a.get_right(), end=obj_b.get_left(), color=YELLOW_C, buff=0.1)
        
        f_ab = MathTex(r"\vec{F}_{AB}").next_to(arrow_to_left, UP, buff=0.2)
        f_ba = MathTex(r"\vec{F}_{BA}").next_to(arrow_to_right, DOWN, buff=0.2)
        
        self.play(Write(title4))
        self.play(Create(obj_a), Create(obj_b), Write(text_a), Write(text_b))
        self.wait(0.5)
        
        self.play(GrowArrow(arrow_to_left), Write(f_ab))
        self.play(GrowArrow(arrow_to_right), Write(f_ba))
        
        note = Text("Equal magnitude, opposite direction", 
                    font_size=28, width=config.frame_width - 2, color=GREY_A)
        note.to_edge(DOWN, buff=1)
        
        self.play(FadeIn(note))
        self.wait(2)
        
        # Final Clear
        self.play(FadeOut(*self.mobjects))