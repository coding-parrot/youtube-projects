from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class HierarchicalWALReplication(Scene):
    def construct(self):
        def make_node(label, w=2.8, h=1.0, fill="#171717", text_color=WHITE, fs=28):
            box = RoundedRectangle(width=w, height=h, corner_radius=0.24, stroke_width=2)
            box.set_fill(fill, opacity=1)
            box.set_stroke(WHITE, width=2)
            txt = Text(label, font_size=fs, color=text_color)
            txt.move_to(box.get_center())
            return VGroup(box, txt)

        def wal_arrow(start, end):
            return Arrow(
                start=start,
                end=end,
                buff=0.14,
                stroke_width=2.8,
                max_tip_length_to_length_ratio=0.16,
                color=WHITE,
            )

        title = Text("PostgreSQL Cascading Replication", font_size=42, color=WHITE).to_edge(UP)

        primary = make_node("PRIMARY", w=3.2, h=1.1, fill="#0398fc", text_color=WHITE, fs=30)
        primary.move_to(UP * 3.0)

        rep_l2_left = make_node("READ\nREPLICA", w=3.0, h=1.2, fill="#ffb30f", text_color=BLACK, fs=27)
        rep_l2_right = make_node("READ\nREPLICA", w=3.0, h=1.2, fill="#ffb30f", text_color=BLACK, fs=27)
        rep_l2_left.move_to(LEFT * 3.0 + UP * 0.9)
        rep_l2_right.move_to(RIGHT * 3.0 + UP * 0.9)
        level2 = VGroup(rep_l2_left, rep_l2_right)

        read_left_1 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_left_2 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_right_1 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_right_2 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)

        read_left_1.move_to(LEFT * 4.5 + DOWN * 1.6)
        read_left_2.move_to(LEFT * 1.5 + DOWN * 1.6)
        read_right_1.move_to(RIGHT * 1.5 + DOWN * 1.6)
        read_right_2.move_to(RIGHT * 4.5 + DOWN * 1.6)
        reads = VGroup(read_left_1, read_left_2, read_right_1, read_right_2)

        ellipsis_top = Text("...", font_size=42, color=WHITE).move_to(ORIGIN + UP * 1.0)
        ellipsis_bottom_left = Text("...", font_size=42, color=WHITE).move_to(LEFT * 3.0 + DOWN * 1.6)
        ellipsis_bottom_right = Text("...", font_size=42, color=WHITE).move_to(RIGHT * 3.0 + DOWN * 1.6)

        a_p_l = wal_arrow(primary.get_bottom() + LEFT * 0.65, rep_l2_left.get_top() + RIGHT * 0.35)
        a_p_r = wal_arrow(primary.get_bottom() + RIGHT * 0.65, rep_l2_right.get_top() + LEFT * 0.35)
        a_l_1 = wal_arrow(rep_l2_left.get_bottom() + LEFT * 0.45, read_left_1.get_top() + RIGHT * 0.25)
        a_l_2 = wal_arrow(rep_l2_left.get_bottom() + RIGHT * 0.45, read_left_2.get_top() + LEFT * 0.25)
        a_r_1 = wal_arrow(rep_l2_right.get_bottom() + LEFT * 0.45, read_right_1.get_top() + RIGHT * 0.25)
        a_r_2 = wal_arrow(rep_l2_right.get_bottom() + RIGHT * 0.45, read_right_2.get_top() + LEFT * 0.25)

        top_arrows = VGroup(a_p_l, a_p_r)
        bottom_arrows = VGroup(a_l_1, a_l_2, a_r_1, a_r_2)

        self.play(FadeIn(title), run_time=0.8)
        self.play(FadeIn(primary), run_time=0.6)
        self.play(FadeIn(level2), FadeIn(ellipsis_top), run_time=0.8)
        self.play(FadeIn(reads), FadeIn(ellipsis_bottom_left), FadeIn(ellipsis_bottom_right), run_time=0.9)

        self.play(LaggedStart(*[Create(a) for a in top_arrows], lag_ratio=0.15), run_time=0.8)
        self.play(LaggedStart(*[Create(a) for a in bottom_arrows], lag_ratio=0.1), run_time=0.9)

        wal_events_top = VGroup(*[Dot(radius=0.09, color=YELLOW) for _ in top_arrows])
        for dot, arrow in zip(wal_events_top, top_arrows):
            dot.move_to(arrow.get_start())
        self.play(FadeIn(wal_events_top), run_time=0.2)

        for _ in range(3):
            self.play(
                *[MoveAlongPath(dot, arrow, rate_func=linear) for dot, arrow in zip(wal_events_top, top_arrows)],
                run_time=0.8,
            )
            for dot, arrow in zip(wal_events_top, top_arrows):
                dot.move_to(arrow.get_start())

            branch_dots = VGroup(*[Dot(radius=0.08, color="#7df9ff") for _ in bottom_arrows])
            for dot, arrow in zip(branch_dots, bottom_arrows):
                dot.move_to(arrow.get_start())
            self.play(FadeIn(branch_dots), run_time=0.15)
            self.play(
                *[MoveAlongPath(dot, arrow, rate_func=linear) for dot, arrow in zip(branch_dots, bottom_arrows)],
                run_time=0.9,
            )
            self.play(FadeOut(branch_dots), run_time=0.15)

        self.play(FadeOut(wal_events_top), run_time=0.2)

        self.play(
            primary[0].animate.set_stroke(YELLOW, width=4),
            rep_l2_left[0].animate.set_stroke(YELLOW, width=4),
            rep_l2_right[0].animate.set_stroke(YELLOW, width=4),
            run_time=0.3,
        )
        self.play(
            reads[0][0].animate.set_stroke(GREEN, width=4),
            reads[1][0].animate.set_stroke(GREEN, width=4),
            reads[2][0].animate.set_stroke(GREEN, width=4),
            reads[3][0].animate.set_stroke(GREEN, width=4),
            run_time=0.4,
        )
        self.wait(0.8)
