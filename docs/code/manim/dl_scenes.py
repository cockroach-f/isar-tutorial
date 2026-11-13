"""第 6 章 自注意力（例题 6.1）与第 7 章 DB-SSIT 的 MixConv 多尺度预处理。"""
from common import *


class M12_SelfAttention(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 12  自注意力三步：打分 → 按行 softmax → 加权汇总"))
        X = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        tc = [BLUE_C, GREEN_C, ORANGE]
        # 左：二维平面
        pl = Axes(x_range=[0, 1.25, 0.5], y_range=[0, 1.25, 0.5], x_length=3.6, y_length=3.6, tips=False,
                  axis_config={"stroke_width": 2, "include_ticks": True}).move_to([-4.6, 0.1, 0])
        grid = NumberPlane(x_range=[0, 1.25, 0.25], y_range=[0, 1.25, 0.25], x_length=3.6, y_length=3.6,
                           background_line_style={"stroke_color": GREY_E, "stroke_width": 1},
                           axis_config={"stroke_opacity": 0}).move_to(pl)
        o = pl.c2p(0, 0)
        vecs = VGroup(*[Arrow(o, pl.c2p(*X[i]), buff=0, color=tc[i], stroke_width=5) for i in range(3)])
        vl = VGroup(MT(r"\mathbf x_1=[1,0]", 24, tc[0]).next_to(pl.c2p(1, 0), DOWN, buff=0.15),
                    MT(r"\mathbf x_2=[0,1]", 24, tc[1]).next_to(pl.c2p(0, 1), RIGHT, buff=0.15),
                    MT(r"\mathbf x_3=[1,1]", 24, tc[2]).next_to(pl.c2p(1, 1), UP, buff=0.1))
        self.play(FadeIn(grid), Create(pl), GrowArrow(vecs[0]), GrowArrow(vecs[1]), GrowArrow(vecs[2]), FadeIn(vl))
        f = MT(r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^T}{\sqrt d}\right)V", 32)
        f.move_to([2.6, 2.45, 0])
        cap.say("例题 6.1：3 个 token，d = 2，取 W_Q = W_K = W_V = I，于是 Q = K = V = X")
        self.play(FadeIn(f))
        self.wait(1.5)

        # 中：3×3 矩阵
        cs = 1.0
        c0 = np.array([1.2, -0.3, 0])

        def cell(i, j):
            return c0 + np.array([(j - 1) * cs, (1 - i) * cs, 0])
        sq = VGroup(*[Square(side_length=cs, stroke_color=GREY_B, stroke_width=1.5).move_to(cell(i, j))
                      for i in range(3) for j in range(3)])
        rl = VGroup(*[MT(rf"\mathbf q_{i + 1}", 26, tc[i]).next_to(cell(i, 0), LEFT, buff=0.6) for i in range(3)])
        cl = VGroup(*[MT(rf"\mathbf k_{j + 1}", 26, tc[j]).next_to(cell(0, j), UP, buff=0.55) for j in range(3)])
        self.play(Create(sq), FadeIn(rl, cl))
        dots = X @ X.T
        nums = VGroup()
        cap.say("第 1 步 打分：S_ij = q_i · k_j，越相似分数越高")
        for i in range(3):
            for j in range(3):
                hl = VGroup(SurroundingRectangle(rl[i], color=YELLOW, buff=0.05),
                            SurroundingRectangle(cl[j], color=YELLOW, buff=0.05))
                n = MT(f"{dots[i, j]:g}", 30).move_to(cell(i, j))
                rt = 0.35 if (i, j) != (0, 0) else 0.8
                self.play(FadeIn(hl), FadeIn(n), run_time=rt)
                self.remove(hl)
                nums.add(n)
        self.wait(0.8)
        S = dots / np.sqrt(2)
        nS = VGroup(*[MT(f"{S[i, j]:.2f}", 28).move_to(cell(i, j)) for i in range(3) for j in range(3)])
        dv = MT(r"\div\sqrt2", 30, YELLOW).next_to(sq, RIGHT, buff=0.3)
        cap.say("除以 √d = √2，防止点积过大、softmax 过尖")
        self.play(FadeIn(dv), Transform(nums, nS))
        self.wait(1.2)
        A = np.exp(S) / np.exp(S).sum(1, keepdims=True)
        cap.say("第 2 步 对每一行做 softmax：每个查询的权重之和为 1")
        fills = VGroup()
        for i in range(3):
            row = SurroundingRectangle(VGroup(*[sq[3 * i + j] for j in range(3)]), color=tc[i], buff=0.03)
            nA = VGroup(*[MT(f"{A[i, j]:.2f}", 28).move_to(cell(i, j)) for j in range(3)])
            fl = VGroup(*[Square(side_length=cs * 0.96, stroke_width=0, fill_color=TEAL,
                                 fill_opacity=0.15 + 0.85 * A[i, j] / 0.6).move_to(cell(i, j)) for j in range(3)])
            self.play(Create(row), run_time=0.4)
            self.play(FadeIn(fl), *[Transform(nums[3 * i + j], nA[j]) for j in range(3)], run_time=0.9)
            self.play(FadeOut(row), run_time=0.3)
            fills.add(fl)
            self.bring_to_front(nums)
        self.play(FadeOut(dv))
        self.wait(1)

        # 第 3 步：加权汇总
        cap.say("第 3 步 输出第 i 行 = 所有 value 按第 i 行权重的加权和")
        outs = A @ X
        chains = VGroup()
        for i in range(3):
            row = SurroundingRectangle(VGroup(*[sq[3 * i + j] for j in range(3)]), color=tc[i], buff=0.03)
            self.play(Create(row), run_time=0.4)
            p = o
            segs = VGroup()
            for j in range(3):
                q = p + (pl.c2p(*X[j]) - o) * A[i, j]
                segs.add(Arrow(p, q, buff=0, color=tc[j], stroke_width=4, max_tip_length_to_length_ratio=0.25))
                p = q
            res = Dot(pl.c2p(*outs[i]), color=tc[i], radius=0.09)
            rlab = MT(rf"\text{{out}}_{i + 1}=[{outs[i, 0]:.2f},\ {outs[i, 1]:.2f}]", 28, tc[i])
            rlab.move_to([4.9, 0.7 - 0.75 * i, 0])
            rt = 2.0 if i == 0 else 1.2
            self.play(LaggedStart(*[GrowArrow(s) for s in segs], lag_ratio=0.6), run_time=rt)
            self.play(FadeIn(res), TransformFromCopy(res, rlab), run_time=0.6)
            if i == 0:
                cap.say("token 1 = 0.40·x₁ + 0.20·x₂ + 0.40·x₃ = [0.80, 0.60]：吸收了相似的 token 3")
                self.wait(2.5)
            self.play(FadeOut(segs), FadeOut(row), run_time=0.4)
            chains.add(res, rlab)
        cap.say("每个输出都融合了全部 token 的信息：一步就能建模远距离关系，代价是 N² 个分数")
        self.wait(3.5)


def sat_dots(tile, pts, color, rad=0.035):
    """在方块 tile 上按归一化坐标 pts∈[-1,1]² 画亮点。"""
    c, s = tile.get_center(), tile.width / 2 * 0.85
    return VGroup(*[Dot(c + np.array([x * s, y * s, 0]), radius=rad, color=color) for x, y in pts])


class M13_MixConv(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 13  MixConv：三组通道用 3×3 / 5×5 / 7×7 三种尺寸的核"))
        # 卫星点目标（本体 + 两块太阳翼）
        pts = [(x, y) for x in np.linspace(-0.2, 0.2, 3) for y in np.linspace(-0.25, 0.25, 3)]
        pts += [(x, y) for x in np.linspace(-0.95, -0.4, 5) for y in (-0.08, 0.08)]
        pts += [(x, y) for x in np.linspace(0.4, 0.95, 5) for y in (-0.08, 0.08)]
        n = 12
        tw = 1.75
        gcol = [BLUE_C, GREEN_C, ORANGE]
        names = [("A", "B"), ("C", "D"), ("E", "F")]
        ks = [3, 5, 7]
        ys = [1.75, -0.2, -2.15]
        tiles, labels = VGroup(), VGroup()
        for g in range(3):
            for k in range(2):
                t = Square(side_length=tw, stroke_color=gcol[g], stroke_width=2, fill_color=BLACK, fill_opacity=1)
                t.move_to([-5.3 + 0.28 * k, ys[g] - 0.2 * k, 0])
                d = sat_dots(t, pts, interpolate_color(GREY_B, gcol[g], 0.5 + 0.3 * k))
                tiles.add(VGroup(t, d))
            labels.add(ZH(f"特征 {names[g][0]}、{names[g][1]}", 20, gcol[g]).next_to(tiles[-1], RIGHT, buff=0.12)
                       .shift(UP * 0.55))
        hd = ZH("6 维极化特征 A–F，平均分成 3 组", 22, GREY_A).move_to([-4.5, 2.95, 0])
        cap.say("DB-SSIT 预处理：A–F 六个特征通道平均分成 3 组，每组 2 个通道")
        self.play(FadeIn(hd), LaggedStart(*[FadeIn(t) for t in tiles], lag_ratio=0.15), run_time=2)
        self.play(FadeIn(labels))
        self.wait(1)
        # 卷积窗口在前面的那张 tile 上滑动
        cell = tw / n
        front = [tiles[2 * g + 1][0] for g in range(3)]
        kt = ValueTracker(0.0)
        path = [(r, c) for r in range(0, n - 6, 2) for c in (range(0, n - 6) if (r // 2) % 2 == 0 else range(n - 7, -1, -1))]

        def win(g):
            t = kt.get_value()
            idx = min(len(path) - 1, int(t))
            r, c = path[idx]
            k = ks[g]
            off = (7 - k) / 2
            tl = front[g].get_corner(UL)
            cen = tl + np.array([(c + off + k / 2) * cell, -(r + off + k / 2) * cell, 0])
            return Square(side_length=k * cell, color=YELLOW, stroke_width=4).move_to(cen)
        wins = [always_redraw(lambda g=g: win(g)) for g in range(3)]
        klab = VGroup(*[MT(rf"{k}\times{k}", 28, YELLOW).next_to(front[g], RIGHT, buff=0.25).shift(DOWN * 0.25)
                        for g, k in enumerate(ks)])
        self.add(*wins)
        self.play(FadeIn(klab))
        cap.say("小核盯住单个散射点的细节，大核一次覆盖整块太阳翼的轮廓")
        self.play(kt.animate.set_value(len(path) - 1), run_time=7, rate_func=linear)

        # 输出：拼接成 32 通道
        arrows = VGroup(*[Arrow(klab[g].get_right() + RIGHT * 0.05, [0.0, ys[g] - 0.1, 0], buff=0.1, color=GREY_B,
                                stroke_width=3) for g in range(3)])
        outs = VGroup()
        for g in range(3):
            st = VGroup(*[Square(side_length=1.2, stroke_color=gcol[g], stroke_width=1.2, fill_color=BLACK,
                                 fill_opacity=0.9).move_to([0.55 + 0.06 * j, ys[g] - 0.1 - 0.05 * j, 0])
                          for j in range(10)])
            outs.add(st)
        self.play(GrowArrow(arrows[0]), GrowArrow(arrows[1]), GrowArrow(arrows[2]),
                  LaggedStart(*[FadeIn(o) for o in outs], lag_ratio=0.2), run_time=1.6)
        cat = VGroup(*[Square(side_length=1.6, stroke_color=gcol[j * 3 // 32], stroke_width=1, fill_color=BLACK,
                              fill_opacity=0.9).move_to([3.1 + 0.035 * j, 0.5 - 0.03 * j, 0]) for j in range(32)])
        catl = ZH("拼接：32 通道", 22).next_to(cat, UP, buff=0.2)
        cap.say("三组输出沿通道拼接，得到 32 通道的多尺度极化–空间特征")
        self.play(ReplacementTransform(outs, cat), FadeOut(arrows), run_time=1.8)
        self.play(FadeIn(catl))
        self.wait(1.2)
        # BN + 池化 + 1×1 卷积
        pool = VGroup(*[Square(side_length=0.8, stroke_color=gcol[j * 3 // 32], stroke_width=1, fill_color=BLACK,
                               fill_opacity=0.9).move_to([3.0 + 0.03 * j, -1.7 - 0.02 * j, 0]) for j in range(32)])
        pl = ZH("BN + 2×2 最大池化", 20, GREY_A).next_to(pool, LEFT, buff=0.3)
        cap.say("BN + 2×2 最大池化（步长 2）把尺寸减半")
        self.play(TransformFromCopy(cat, pool), FadeIn(pl), run_time=1.5)
        c6 = VGroup(*[Square(side_length=0.8, stroke_color=TEAL, stroke_width=1.5, fill_color=BLACK, fill_opacity=0.9)
                      .move_to([5.0 + 0.07 * j, -1.7 - 0.05 * j, 0]) for j in range(6)])
        c3 = VGroup(*[Square(side_length=0.8, stroke_color=PINK, stroke_width=1.5, fill_color=BLACK, fill_opacity=0.9)
                      .move_to([6.2 + 0.07 * j, -1.7 - 0.05 * j, 0]) for j in range(3)])
        l6 = MT(r"6", 26, TEAL).next_to(c6, UP, buff=0.12)
        l3 = MT(r"3", 26, PINK).next_to(c3, UP, buff=0.12)
        cap.say("两个 1×1 卷积压缩通道：32 → 6（保留关键极化信息）→ 3（匹配后续模块）")
        self.play(TransformFromCopy(pool, c6), FadeIn(l6), run_time=1.2)
        self.play(TransformFromCopy(c6, c3), FadeIn(l3), run_time=1.2)
        self.wait(3)
