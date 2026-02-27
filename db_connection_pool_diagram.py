from manim import *

# Keep a 16:9 render with a taller frame so vertical layouts stay visible.
config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class DBConnectionPoolDiagram(Scene):
    def construct(self):
        # ---------- Helpers ----------
        def make_node(
            label: str,
            width=3.0,
            height=1.0,
            fill_color=None,
            text_color=WHITE,
            font_size=30,
        ):
            box = RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.2,
                stroke_width=2,
            )
            if fill_color:
                box.set_fill(fill_color, opacity=1)
                box.set_stroke(fill_color)
            else:
                box.set_fill(opacity=0)
                box.set_stroke(WHITE)

            text = Text(label, font_size=font_size, color=text_color)
            text.move_to(box.get_center())
            return VGroup(box, text)

        def make_connection(slot_label: str):
            slot = RoundedRectangle(
                width=2.6,
                height=0.8,
                corner_radius=0.15,
                stroke_width=2,
            )
            slot.set_fill("#ffd166", opacity=1)
            slot.set_stroke("#ffd166")
            txt = Text(slot_label, font_size=24, color=BLACK)
            txt.move_to(slot.get_center())
            return VGroup(slot, txt)

        def make_request(color=YELLOW):
            return Dot(radius=0.16, color=color)

        # ---------- Main blocks ----------
        incoming = make_node(
            "Clients",
            width=3.1,
            height=1.2,
            fill_color="#5c7cfa",
            text_color=WHITE,
            font_size=30,
        )
        incoming.move_to(LEFT * 5.2)

        pool_shell = RoundedRectangle(
            width=4.8,
            height=5.6,
            corner_radius=0.2,
            stroke_width=2,
        )
        pool_shell.set_fill(opacity=0)
        pool_shell.set_stroke(WHITE)

        pool_title = Text("DB Connection Pool", font_size=30, color=WHITE)
        pool_title.move_to(pool_shell.get_top() + DOWN * 0.45)

        connections = VGroup(*[make_connection(f"Conn {i}") for i in range(1, 5)])
        connections.arrange(DOWN, buff=0.30)
        connections.move_to(pool_shell.get_center() + DOWN * 0.45)

        pool = VGroup(pool_shell, pool_title, connections)
        pool.move_to(ORIGIN)

        database = make_node(
            "Database",
            width=2.8,
            height=1.0,
            fill_color="#06d6a0",
            text_color=BLACK,
            font_size=30,
        )
        database.move_to(RIGHT * 5.2)

        # ---------- Static arrows ----------
        request_arrow = Arrow(
            start=np.array([incoming.get_right()[0], pool_shell.get_center()[1], 0]),
            end=np.array([pool_shell.get_left()[0], pool_shell.get_center()[1], 0]),
            buff=0.2,
            stroke_width=3,
            max_tip_length_to_length_ratio=0.12,
        )

        db_arrows = VGroup()
        for conn in connections:
            db_arrows.add(
                Arrow(
                    start=conn.get_right(),
                    end=database.get_left(),
                    buff=0.2,
                    stroke_width=2.5,
                    max_tip_length_to_length_ratio=0.12,
                )
            )

        # ---------- Draw ----------
        self.play(FadeIn(incoming), FadeIn(pool_shell), FadeIn(pool_title), FadeIn(database))
        self.play(LaggedStart(*[FadeIn(c) for c in connections], lag_ratio=0.08))
        self.play(Create(request_arrow))
        self.play(LaggedStart(*[Create(a) for a in db_arrows], lag_ratio=0.06))

        # ---------- Request lifecycle animation ----------
        status = Text("Acquire connection", font_size=32, color=YELLOW)
        status.to_edge(DOWN)
        self.play(FadeIn(status), run_time=0.3)

        total_requests = 8
        for i in range(total_requests):
            conn_index = i % len(connections)
            chosen = connections[conn_index]

            req = make_request(color=YELLOW)
            req.move_to(incoming.get_right() + RIGHT * 0.15)

            original_color = chosen[0].get_fill_color()
            busy_color = "#ff6b6b"

            # Acquire in 2 hops: follow incoming arrow into pool, then route to selected connection
            self.play(
                MoveAlongPath(
                    req,
                    Line(req.get_center(), request_arrow.get_end() + RIGHT * 0.06),
                    rate_func=linear,
                ),
                run_time=0.3,
            )

            self.play(
                MoveAlongPath(
                    req,
                    Line(req.get_center(), chosen.get_left() + RIGHT * 0.15),
                    rate_func=linear,
                ),
                chosen[0].animate.set_fill(busy_color, opacity=1),
                run_time=0.3,
            )

            # Use connection (connection -> DB)
            self.play(
                MoveAlongPath(
                    req,
                    Line(chosen.get_right() + RIGHT * 0.05, database.get_left() + LEFT * 0.05),
                    rate_func=linear,
                ),
                run_time=0.45,
            )

            # Release: return to pool and mark as free
            self.play(
                MoveAlongPath(
                    req,
                    Line(database.get_left() + LEFT * 0.05, chosen.get_center()),
                    rate_func=linear,
                ),
                chosen[0].animate.set_fill(original_color, opacity=1),
                run_time=0.45,
            )

            self.play(FadeOut(req), run_time=0.15)

            if i == total_requests // 2 - 1:
                self.play(Transform(status, Text("Release after use", font_size=32, color=GREEN).to_edge(DOWN)))

        self.play(FadeOut(status), run_time=0.25)
        self.wait(0.5)
