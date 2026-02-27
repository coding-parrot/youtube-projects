from manim import *

config.pixel_width = 1920
config.pixel_height = 1080
config.frame_height = 10.5
config.frame_width = config.frame_height * 16 / 9


class RequestCollapsingInCache(Scene):
    def construct(self):
        def make_box(label, w=2.8, h=1.0, fill="#2b2d42", text_color=WHITE, fs=30):
            rect = RoundedRectangle(width=w, height=h, corner_radius=0.16, stroke_width=2)
            rect.set_fill(fill, opacity=1)
            rect.set_stroke(fill)
            txt = Text(label, font_size=fs, color=text_color)
            txt.move_to(rect.get_center())
            return VGroup(rect, txt)

        def req_dot(color=YELLOW, r=0.12):
            return Dot(radius=r, color=color)

        # ---------- Nodes ----------
        clients = VGroup(*[make_box(f"Client {i}", w=2.3, h=0.8, fill="#5c7cfa", fs=24) for i in range(1, 4)])
        clients.arrange(DOWN, buff=0.35).move_to(LEFT * 5.2)

        cache = make_box("Cache", w=3.2, h=1.2, fill="#f4a261", text_color=BLACK)
        cache.move_to(ORIGIN + UP * 0.8)

        db = make_box("Database", w=3.2, h=1.2, fill="#06d6a0", text_color=BLACK)
        db.move_to(RIGHT * 5.1 + UP * 0.8)

        title = Text("Request Collapsing", font_size=42, color=WHITE).to_edge(UP)

        # ---------- Compact table (in-cache key/value entry) ----------
        table_box = RoundedRectangle(width=5.8, height=1.9, corner_radius=0.12, stroke_width=2)
        table_box.set_stroke(GRAY_B)
        table_box.set_fill("#1c1f2b", opacity=0.45)
        table_box.next_to(cache, DOWN, buff=0.55)

        header_line = Line(table_box.get_left() + RIGHT * 0.25 + UP * 0.25, table_box.get_right() + LEFT * 0.25 + UP * 0.25)
        header_line.set_stroke(GRAY_B, width=2)
        divider = Line(table_box.get_center() + UP * 0.7, table_box.get_center() + DOWN * 0.7)
        divider.set_stroke(GRAY_B, width=2)

        key_head = Text("KEY", font_size=24, color=GRAY_A)
        val_head = Text("VALUE", font_size=24, color=GRAY_A)
        key_head.move_to(np.array([table_box.get_left()[0] + 1.2, table_box.get_top()[1] - 0.33, 0]))
        val_head.move_to(np.array([table_box.get_right()[0] - 1.2, table_box.get_top()[1] - 0.33, 0]))

        key_cell = Text("user:42", font_size=34, color=WHITE)
        val_cell = Text("Promise", font_size=34, color=YELLOW)
        key_cell.move_to(np.array([key_head.get_center()[0], table_box.get_bottom()[1] + 0.55, 0]))
        val_cell.move_to(np.array([val_head.get_center()[0], table_box.get_bottom()[1] + 0.55, 0]))

        # ---------- Arrows ----------
        arrows_to_cache = VGroup(*[
            Arrow(c.get_right(), cache.get_left(), buff=0.16, stroke_width=2.6)
            for c in clients
        ])

        y_mid = cache.get_center()[1]
        cache_to_db = Arrow(
            start=np.array([cache.get_right()[0], y_mid, 0]),
            end=np.array([db.get_left()[0], y_mid, 0]),
            buff=0.2,
            stroke_width=3,
            color=ORANGE,
        )
        db_to_cache = Arrow(
            start=np.array([db.get_left()[0], y_mid, 0]),
            end=np.array([cache.get_right()[0], y_mid, 0]),
            buff=0.2,
            stroke_width=3,
            color=GREEN,
        )

        # ---------- Draw ----------
        self.play(FadeIn(title), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(c) for c in clients], lag_ratio=0.12), FadeIn(cache), FadeIn(db), run_time=1.4)
        self.play(LaggedStart(*[Create(a) for a in arrows_to_cache], lag_ratio=0.08), run_time=1.2)
        self.play(FadeIn(table_box), Create(header_line), Create(divider), FadeIn(key_head), FadeIn(val_head), run_time=0.8)

        # ---------- First request creates promise + one DB call ----------
        req1 = req_dot(color=YELLOW)
        req1.move_to(arrows_to_cache[0].get_start())
        self.play(FadeIn(req1), run_time=0.3)
        self.play(MoveAlongPath(req1, arrows_to_cache[0], rate_func=linear), run_time=0.9)

        self.play(
            FadeIn(key_cell),
            FadeIn(val_cell),
            table_box.animate.set_stroke(YELLOW, width=3),
            run_time=0.7,
        )

        self.play(Create(cache_to_db), run_time=0.5)
        db_req = req_dot(color=ORANGE)
        db_req.move_to(cache_to_db.get_start())
        self.play(FadeIn(db_req), run_time=0.2)
        self.play(MoveAlongPath(db_req, cache_to_db, rate_func=linear), run_time=1)
        self.play(FadeOut(db_req), FadeOut(cache_to_db), run_time=0.4)

        # ---------- Collapsed requests: same promise returned ----------
        req2, req3 = req_dot(color=YELLOW), req_dot(color=YELLOW)
        req2.move_to(arrows_to_cache[1].get_start())
        req3.move_to(arrows_to_cache[2].get_start())
        self.play(FadeIn(req2), FadeIn(req3), run_time=0.4)
        self.play(
            MoveAlongPath(req2, arrows_to_cache[1], rate_func=linear),
            MoveAlongPath(req3, arrows_to_cache[2], rate_func=linear),
            run_time=0.9,
        )
        self.play(FadeOut(arrows_to_cache), run_time=0.4)

        # ---------- DB resolves once ----------
        self.play(Create(db_to_cache), run_time=0.5)
        db_res = req_dot(color=GREEN)
        db_res.move_to(db_to_cache.get_start())
        self.play(FadeIn(db_res), run_time=0.2)
        self.play(MoveAlongPath(db_res, db_to_cache, rate_func=linear), run_time=1)
        self.play(FadeOut(db_res), run_time=0.2)

        done_cell = Text("Data Ready", font_size=32, color=GREEN)
        done_cell.move_to(val_cell.get_center())
        self.play(Transform(val_cell, done_cell), table_box.animate.set_stroke(GREEN, width=3), run_time=0.7)

        # ---------- Propagate completion to all clients ----------
        fanout_arrows = VGroup(*[
            Arrow(cache.get_left(), c.get_right(), buff=0.16, stroke_width=2.2, color=GREEN)
            for c in clients
        ])
        self.play(LaggedStart(*[Create(a) for a in fanout_arrows], lag_ratio=0.08), run_time=0.9)

        self.play(
            MoveAlongPath(req1, fanout_arrows[0], rate_func=linear),
            MoveAlongPath(req2, fanout_arrows[1], rate_func=linear),
            MoveAlongPath(req3, fanout_arrows[2], rate_func=linear),
            run_time=1.1,
        )

        self.play(
            clients[0][0].animate.set_stroke(GREEN, width=4),
            clients[1][0].animate.set_stroke(GREEN, width=4),
            clients[2][0].animate.set_stroke(GREEN, width=4),
            run_time=0.4,
        )
        self.play(
            clients[0][0].animate.set_stroke("#5c7cfa", width=2),
            clients[1][0].animate.set_stroke("#5c7cfa", width=2),
            clients[2][0].animate.set_stroke("#5c7cfa", width=2),
            run_time=0.4,
        )

        self.wait(1.2)
