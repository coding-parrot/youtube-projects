from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class HierarchicalWALReplication(Scene):
    def construct(self):
        def make_node(label, w=2.8, h=1.0, fill="#7a3f1d", text_color=WHITE, fs=28):
            box = RoundedRectangle(width=w, height=h, corner_radius=0.28, stroke_width=2)
            box.set_fill(fill, opacity=1)
            box.set_stroke(WHITE, width=2)
            txt = Text(label, font_size=fs, color=text_color)
            txt.move_to(box.get_center())
            return VGroup(box, txt)

        def wal_arrow(start, end):
            return CurvedArrow(
                start_point=start,
                end_point=end,
                angle=-0.35,
                stroke_width=2.8,
                tip_length=0.18,
                color=WHITE,
            )

        def wal_label_for(arrow):
            label = Text("WAL", font_size=22, color=WHITE)
            mid = arrow.point_from_proportion(0.52)
            label.move_to(mid + UP * 0.25)
            return label

        title = Text("PostgreSQL Cascading Replication", font_size=42, color=WHITE).to_edge(UP)

        primary = make_node("PRIMARY", w=3.2, h=1.1, fill="#c36f45", fs=30)
        primary.move_to(UP * 3.0)

        int_left = make_node("INTERMEDIATE\nREPLICA", w=3.2, h=1.2, fill="#a75f38", fs=27)
        int_right = make_node("INTERMEDIATE\nREPLICA", w=3.2, h=1.2, fill="#a75f38", fs=27)
        int_left.move_to(LEFT * 4.2 + UP * 0.7)
        int_right.move_to(RIGHT * 4.2 + UP * 0.7)
        intermediates = VGroup(int_left, int_right)

        read_left_1 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_left_2 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_right_1 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)
        read_right_2 = make_node("READ\nREPLICA", w=2.7, h=1.0, fill="#171717", fs=26)

        read_left_1.move_to(LEFT * 6.0 + DOWN * 2.0)
        read_left_2.move_to(LEFT * 2.2 + DOWN * 2.0)
        read_right_1.move_to(RIGHT * 2.2 + DOWN * 2.0)
        read_right_2.move_to(RIGHT * 6.0 + DOWN * 2.0)
        reads = VGroup(read_left_1, read_left_2, read_right_1, read_right_2)

        ellipsis_top = Text("...", font_size=44, color=WHITE).move_to(ORIGIN + UP * 0.9)
        ellipsis_bottom_left = Text("...", font_size=44, color=WHITE).move_to(LEFT * 4.1 + DOWN * 2.0)
        ellipsis_bottom_right = Text("...", font_size=44, color=WHITE).move_to(RIGHT * 4.1 + DOWN * 2.0)

        a_p_l = wal_arrow(primary.get_bottom() + LEFT * 0.8, int_left.get_top() + RIGHT * 0.45)
        a_p_r = wal_arrow(primary.get_bottom() + RIGHT * 0.8, int_right.get_top() + LEFT * 0.45)
        a_l_1 = wal_arrow(int_left.get_bottom() + LEFT * 0.6, read_left_1.get_top() + RIGHT * 0.3)
        a_l_2 = wal_arrow(int_left.get_bottom() + RIGHT * 0.6, read_left_2.get_top() + LEFT * 0.3)
        a_r_1 = wal_arrow(int_right.get_bottom() + LEFT * 0.6, read_right_1.get_top() + RIGHT * 0.3)
        a_r_2 = wal_arrow(int_right.get_bottom() + RIGHT * 0.6, read_right_2.get_top() + LEFT * 0.3)

        top_arrows = VGroup(a_p_l, a_p_r)
        bottom_arrows = VGroup(a_l_1, a_l_2, a_r_1, a_r_2)

        top_labels = VGroup(*[wal_label_for(a) for a in top_arrows])
        bottom_labels = VGroup(*[wal_label_for(a) for a in bottom_arrows])

        self.play(FadeIn(title), run_time=0.8)
        self.play(FadeIn(primary), run_time=0.6)
        self.play(FadeIn(intermediates), FadeIn(ellipsis_top), run_time=0.8)
        self.play(FadeIn(reads), FadeIn(ellipsis_bottom_left), FadeIn(ellipsis_bottom_right), run_time=0.9)

        self.play(LaggedStart(*[Create(a) for a in top_arrows], lag_ratio=0.15), run_time=0.8)
        self.play(FadeIn(top_labels), run_time=0.3)
        self.play(LaggedStart(*[Create(a) for a in bottom_arrows], lag_ratio=0.1), run_time=0.9)
        self.play(FadeIn(bottom_labels), run_time=0.3)

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
            int_left[0].animate.set_stroke(YELLOW, width=4),
            int_right[0].animate.set_stroke(YELLOW, width=4),
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
