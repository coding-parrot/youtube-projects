from manim import *

# Increase both render resolution and camera frame size so lower replicas remain visible.
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class PrimaryToReadReplicas(Scene):
    def construct(self):
        # ---------- Helpers ----------
        def make_node(
            label: str,
            w=2.6,
            h=0.9,                 # reduced height so the extra replica fits in-frame
            font_size=26,          # reduced font size to match the smaller box
            fill_color=None,
            text_color=WHITE,
        ):
            box = RoundedRectangle(
                width=w,
                height=h,
                corner_radius=0.18,
                stroke_width=2,
            )

            if fill_color:
                box.set_fill(fill_color, opacity=1)
                box.set_stroke(fill_color)
            else:
                box.set_fill(opacity=0)
                box.set_stroke(WHITE)

            txt = Text(label, font_size=font_size, color=text_color)
            txt.move_to(box.get_center())
            return VGroup(box, txt)

        def make_request_dot(color=YELLOW, r=0.07):
            return Dot(radius=r, color=color)

        # ---------- Labels ----------
        labels = ["Read 1", "Read 2", "Read 3", "...", "Read 50"]

        # ---------- Nodes ----------
        primary = make_node("Primary DB", fill_color="#0398fc", text_color=WHITE)

        reads = VGroup(
            *[make_node(label, fill_color="#ffb30f", text_color=BLACK) for label in labels]
        )

        # Layout: primary left, reads stacked right (use smaller vertical spacing so Read 51 fits)
        primary.move_to(LEFT * 4)
        reads.arrange(DOWN, buff=0.35).move_to(RIGHT * 3.6)

        # ---------- Edges for initial reads ----------
        arrows = VGroup()
        for r in reads:
            a = Arrow(
                start=primary.get_right(),
                end=r.get_left(),
                buff=0.22,
                stroke_width=3,
                max_tip_length_to_length_ratio=0.12,
            )
            arrows.add(a)

        # ---------- Draw ----------
        self.play(FadeIn(primary))
        self.play(LaggedStart(*[FadeIn(r) for r in reads], lag_ratio=0.08))
        self.play(LaggedStart(*[Create(a) for a in arrows], lag_ratio=0.08))
        self.wait(0.2)

        # ============================================================
        # Add Read 51 at the end (without camera zooming)
        # ============================================================

        read51 = make_node("Read 51", fill_color="#ffb30f", text_color=BLACK)
        read51.next_to(reads[-1], DOWN, buff=0.35)

        arrow51 = Arrow(
            start=primary.get_right(),
            end=read51.get_left(),
            buff=0.22,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.12,
        )

        self.play(FadeIn(read51), run_time=0.35)
        self.play(Create(arrow51), run_time=0.45)

        # ---------- Animate moving "requests" (after Read 51 is added) ----------
        all_arrows = VGroup(*arrows, arrow51)
        request_dots = VGroup(*[make_request_dot() for _ in range(len(all_arrows))])
        for dot, arrow in zip(request_dots, all_arrows):
            dot.move_to(arrow.get_start())
        self.play(FadeIn(request_dots), run_time=0.3)

        waves = 3
        for _ in range(waves):
            self.play(
                *[
                    MoveAlongPath(dot, arrow, rate_func=linear)
                    for dot, arrow in zip(request_dots, all_arrows)
                ],
                run_time=1.1,
            )
            for dot, arrow in zip(request_dots, all_arrows):
                dot.move_to(arrow.get_start())
            self.wait(0.1)

        self.play(FadeOut(request_dots), run_time=0.3)

        # ---------- Bombard the Primary DB with write requests from the top ----------
        # Simulates incoming app-server writes (app server itself intentionally not shown).
        x_offsets = [-0.9, -0.3, 0.3, 0.9]
        incoming_dots = VGroup(*[make_request_dot(color=RED_E, r=0.08) for _ in x_offsets])

        spawn_y = config.frame_height / 2 - 0.3
        for dot, x in zip(incoming_dots, x_offsets):
            dot.move_to(np.array([primary.get_center()[0] + x, spawn_y, 0]))

        self.play(FadeIn(incoming_dots), run_time=0.2)

        for _ in range(5):
            impacts = []
            for dot, x in zip(incoming_dots, x_offsets):
                target = primary.get_top() + np.array([x * 0.22, -0.04, 0])
                path = Line(dot.get_center(), target)
                impacts.append(MoveAlongPath(dot, path, rate_func=linear))

            self.play(*impacts, run_time=0.32)
            self.play(primary[0].animate.set_stroke(RED, width=6), run_time=0.08)
            self.play(primary[0].animate.set_stroke("#0398fc", width=2), run_time=0.08)

            for dot, x in zip(incoming_dots, x_offsets):
                dot.move_to(np.array([primary.get_center()[0] + x, spawn_y, 0]))

        self.play(FadeOut(incoming_dots), run_time=0.2)
        self.wait(0.5)
