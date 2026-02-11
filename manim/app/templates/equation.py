from manim import *

def show_equation(scene, latex):
    # Detect block equations (aligned, cases, matrix, etc.)
    is_block = "aligned" in latex or "cases" in latex or "pmatrix" in latex

    eq = MathTex(
        latex,
        font_size=56 if is_block else 64
    )

    if is_block:
        # Block equations should sit higher
        eq.to_edge(UP).shift(DOWN * 1.8)
    else:
        # Single equations can be centered
        eq.move_to(ORIGIN).shift(DOWN * 0.5)

    scene.play(Write(eq))
    scene.wait(2)

    return eq
