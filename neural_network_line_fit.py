from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class NeuralNetworkLearnsLine(Scene):
    def construct(self):
        def node(label, fill, text_color=WHITE, w=1.9, h=0.95, fs=30):
            box = RoundedRectangle(width=w, height=h, corner_radius=0.2, stroke_width=2)
            box.set_fill(fill, opacity=1)
            box.set_stroke(WHITE, width=2)
            txt = Text(label, font_size=fs, color=text_color)
            txt.move_to(box.get_center())
            return VGroup(box, txt)

        title = Text("Neural Network Learning y = m x + C", font_size=40, color=WHITE).to_edge(UP)

        x_node = node("x", fill="#5c7cfa", w=1.4, fs=36)
        mult_node = node("× m", fill="#ffb30f", text_color=BLACK, w=2.0, fs=32)
        add_node = node("+ C", fill="#ffb30f", text_color=BLACK, w=2.0, fs=32)
        yhat_node = node("ŷ", fill="#06d6a0", text_color=BLACK, w=1.6, fs=36)
        y_node = node("y", fill="#ef476f", w=1.4, fs=36)
        loss_node = node("Loss", fill="#7b2cbf", w=2.2, fs=32)

        network = VGroup(x_node, mult_node, add_node, yhat_node)
        network.arrange(RIGHT, buff=1.0).move_to(UP * 0.7)
        y_node.next_to(yhat_node, DOWN, buff=1.5)
        loss_node.next_to(yhat_node, RIGHT, buff=2.2).shift(DOWN * 1.5)

        a1 = Arrow(x_node.get_right(), mult_node.get_left(), buff=0.12, stroke_width=2.8)
        a2 = Arrow(mult_node.get_right(), add_node.get_left(), buff=0.12, stroke_width=2.8)
        a3 = Arrow(add_node.get_right(), yhat_node.get_left(), buff=0.12, stroke_width=2.8)
        compare_arrow = Arrow(yhat_node.get_bottom(), loss_node.get_left() + LEFT * 0.1, buff=0.15, stroke_width=2.6)
        gt_arrow = Arrow(y_node.get_right(), loss_node.get_left() + DOWN * 0.15, buff=0.15, stroke_width=2.6)
        back_m = Arrow(loss_node.get_top(), mult_node.get_bottom(), buff=0.15, stroke_width=2.4, color=ORANGE)
        back_c = Arrow(loss_node.get_top(), add_node.get_bottom(), buff=0.15, stroke_width=2.4, color=ORANGE)

        eq = MathTex(r"\hat{y} = m x + C", font_size=44).next_to(network, DOWN, buff=1.1).shift(LEFT * 2.0)
        m_val = DecimalNumber(0.40, num_decimal_places=2, font_size=38, color=YELLOW)
        c_val = DecimalNumber(1.80, num_decimal_places=2, font_size=38, color=YELLOW)
        loss_val = DecimalNumber(8.60, num_decimal_places=2, font_size=38, color=RED)

        m_label = Text("m:", font_size=30, color=WHITE)
        c_label = Text("C:", font_size=30, color=WHITE)
        l_label = Text("loss:", font_size=30, color=WHITE)

        stats = VGroup(
            VGroup(m_label, m_val).arrange(RIGHT, buff=0.2),
            VGroup(c_label, c_val).arrange(RIGHT, buff=0.2),
            VGroup(l_label, loss_val).arrange(RIGHT, buff=0.2),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        stats.next_to(loss_node, RIGHT, buff=1.0)

        self.play(FadeIn(title), run_time=0.8)
        self.play(FadeIn(network), run_time=1.0)
        self.play(Create(a1), Create(a2), Create(a3), run_time=0.9)
        self.play(FadeIn(y_node), run_time=0.4)
        self.play(FadeIn(loss_node), Create(compare_arrow), Create(gt_arrow), run_time=0.9)
        self.play(Write(eq), FadeIn(stats), run_time=0.9)

        forward_dot = Dot(radius=0.09, color=YELLOW)
        for _ in range(2):
            forward_dot.move_to(a1.get_start())
            self.play(FadeIn(forward_dot), run_time=0.15)
            self.play(MoveAlongPath(forward_dot, a1, rate_func=linear), run_time=0.35)
            self.play(MoveAlongPath(forward_dot, a2, rate_func=linear), run_time=0.35)
            self.play(MoveAlongPath(forward_dot, a3, rate_func=linear), run_time=0.35)
            self.play(MoveAlongPath(forward_dot, compare_arrow, rate_func=linear), run_time=0.45)
            self.play(FadeOut(forward_dot), run_time=0.15)

        epochs = [
            (0.75, 1.45, 5.20),
            (1.10, 1.05, 2.90),
            (1.35, 0.70, 1.40),
            (1.50, 0.50, 0.35),
        ]

        for m_new, c_new, l_new in epochs:
            self.play(Create(back_m), Create(back_c), run_time=0.25)
            self.play(
                m_val.animate.set_value(m_new),
                c_val.animate.set_value(c_new),
                loss_val.animate.set_value(l_new),
                mult_node[0].animate.set_stroke(ORANGE, width=5),
                add_node[0].animate.set_stroke(ORANGE, width=5),
                run_time=0.8,
            )
            self.play(
                mult_node[0].animate.set_stroke(WHITE, width=2),
                add_node[0].animate.set_stroke(WHITE, width=2),
                FadeOut(back_m),
                FadeOut(back_c),
                run_time=0.35,
            )

        final_box = SurroundingRectangle(eq, color=GREEN, buff=0.2, stroke_width=3)
        self.play(Create(final_box), loss_node[0].animate.set_stroke(GREEN, width=4), run_time=0.6)
        self.wait(0.8)
