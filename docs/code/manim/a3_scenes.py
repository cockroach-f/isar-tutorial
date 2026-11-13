"""第 3 章 · Pauli 分解（式 3.2–3.3）与相干矩阵的窗口平均（式 3.4）。"""
from common import *


def pauli(S):
    hh, hv, vv = S
    return np.array([hh + vv, hh - vv, 2 * hv]) / np.sqrt(2)


def cfmt(z):
    z = complex(z)
    re, im = round(z.real, 2), round(z.imag, 2)
    if abs(im) < 1e-9:
        return f"{re:g}"
    if abs(re) < 1e-9:
        return f"{im:g}j"
    return f"{re:g}{im:+g}j"


def smat(S, size=34):
    hh, hv, vv = S
    return MT(r"\mathbf S=\begin{bmatrix}" + f"{cfmt(hh)}&{cfmt(hv)}\\\\{cfmt(hv)}&{cfmt(vv)}" + r"\end{bmatrix}", size)


class M10_Pauli(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 10  Pauli 分解：像“三原色”一样拆散射矩阵"))
        eq = MathTex(r"\mathbf S", r"=", r"\frac{a}{\sqrt2}\begin{bmatrix}1&0\\0&1\end{bmatrix}", r"+",
                r"\frac{b}{\sqrt2}\begin{bmatrix}1&0\\0&-1\end{bmatrix}", r"+",
                r"\frac{c}{\sqrt2}\begin{bmatrix}0&1\\1&0\end{bmatrix}", font_size=36).move_to([0.6, 2.2, 0])
        eq[2].set_color(C_ODD)
        eq[4].set_color(C_EVEN)
        eq[6].set_color(C_CROSS)
        tags = VGroup(ZH("奇次：平板、三面角", 20, C_ODD).next_to(eq[2], DOWN, buff=0.15),
                      ZH("偶次：二面角", 20, C_EVEN).next_to(eq[4], DOWN, buff=0.15),
                      ZH("45° 二面角 / 交叉极化", 20, C_CROSS).next_to(eq[6], DOWN, buff=0.15))
        cap.say("互易时 S 只有 3 个独立复数，总能唯一写成三种标准散射体的加权和（式 3.2）")
        self.play(Write(eq), run_time=2)
        self.play(FadeIn(tags, lag_ratio=0.3))
        self.wait(1.5)
        kvec = MT(r"\mathbf k_{3P}=\begin{bmatrix}a\\b\\c\end{bmatrix}=\frac{1}{\sqrt2}"
                  r"\begin{bmatrix}S_{HH}+S_{VV}\\S_{HH}-S_{VV}\\2S_{HV}\end{bmatrix}", 32).move_to([-3.7, -0.4, 0])
        self.play(FadeIn(kvec))
        cap.say("逐元素比较即可解出 a、b、c，排成列向量就是 Pauli 散射矢量（式 3.3）")
        self.wait(2.5)

        # ---------- 功率条 + 伪彩色 ----------
        ax0 = np.array([0.9, -2.55, 0])
        cols = [C_ODD, C_EVEN, C_CROSS]
        names = [r"|a|^2", r"|b|^2", r"|c|^2"]
        H = 2.6
        tr = [ValueTracker(0.0) for _ in range(3)]
        bars = [always_redraw(lambda i=i: Rectangle(width=0.7, height=max(1e-3, H * tr[i].get_value()),
                                                   stroke_width=0, fill_color=cols[i], fill_opacity=0.9)
                              .move_to(ax0 + RIGHT * 1.05 * i, aligned_edge=DOWN)) for i in range(3)]
        base = Line(ax0 + LEFT * 0.5, ax0 + RIGHT * 2.6, color=GREY_B)
        bl = VGroup(*[MT(names[i], 24, cols[i]).next_to(ax0 + RIGHT * 1.05 * i, DOWN, buff=0.12) for i in range(3)])
        vals = [always_redraw(lambda i=i: DecimalNumber(tr[i].get_value(), num_decimal_places=2, font_size=22)
                              .next_to(bars[i], UP, buff=0.08)) for i in range(3)]
        bh = ZH("各机理功率占比", 20, GREY_B).next_to(base, UP, buff=H + 0.45).shift(RIGHT * 0.0)
        px = always_redraw(lambda: Square(side_length=1.6, stroke_color=WHITE, stroke_width=2, fill_opacity=1,
                                          fill_color=rgb_to_color(np.clip([np.sqrt(tr[1].get_value()),
                                                                           np.sqrt(tr[2].get_value()),
                                                                           np.sqrt(tr[0].get_value())], 0, 1)))
                           .move_to([5.4, -1.1, 0]))
        pxl = ZH("Pauli 伪彩色：R=|b|, G=|c|, B=|a|", 20, GREY_B).move_to([5.4, -2.25, 0])
        fit(pxl, 3.0)
        self.play(Create(base), FadeIn(bl, bh, pxl))
        self.add(*bars, *vals, px)

        cases = [
            ((0.8, 0.1j, -0.6), "例题 3.1：HH 与 VV 反号 → 偶次占 96%，像素显示为红色"),
            ((0.5, 0, 0.5), "平板（HH=VV）：只有 a，像素为蓝色"),
            ((0, 0.5, 0), "45° 二面角（只有 HV）：只有 c，像素为绿色"),
            ((1.0, 0, 0.0), "水平细线（只有 HH）：a、b 各占一半，像素呈品红色"),
        ]
        smobj = None
        for S, txt in cases:
            k = pauli(S)
            p = np.abs(k) ** 2
            p = p / p.sum()
            new_s = smat(S, 34).move_to([-3.7, -2.35, 0]) if smobj is not None else smat(S, 34).move_to([-3.7, -2.35, 0])
            kval = MT(r"\mathbf k_{3P}=[" + ",\\ ".join(cfmt(round(z.real, 4) + 1j * round(z.imag, 4)) for z in k) + "]^T",
                      26, GREY_A).next_to(new_s, UP, buff=0.2)
            grp = VGroup(new_s, kval)
            cap.say(txt)
            if smobj is None:
                self.play(FadeOut(kvec), FadeIn(grp), *[tr[i].animate.set_value(p[i]) for i in range(3)], run_time=1.6)
            else:
                self.play(FadeTransform(smobj, grp), *[tr[i].animate.set_value(p[i]) for i in range(3)], run_time=1.6)
            smobj = grp
            self.wait(2.8)
        cap.say("三个功率之和等于总功率 Span = |S_HH|² + 2|S_HV|² + |S_VV|²，系数 1/√2 保证这一点")
        self.wait(3)


class M11_Coherency(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 11  相干矩阵 T：在窗口里对 k k^H 求平均"))
        rng = np.random.default_rng(7)
        R, Cn, cs = 6, 10, 0.42
        org = np.array([-6.4, -1.6, 0])  # 左下角
        K = np.zeros((R, Cn, 3), complex)
        for r in range(R):
            for c in range(Cn):
                ph = np.exp(1j * rng.uniform(0, 2 * np.pi))
                n = 0.12 * (rng.normal(size=3) + 1j * rng.normal(size=3))
                if c < 5:   # 二面角区（本体）
                    K[r, c] = ph * np.array([0.15, 1.0, 0.1]) + n
                else:       # 平板区（太阳翼）
                    K[r, c] = ph * np.array([1.0, 0.1, 0.12]) + n
        grid = VGroup()
        for r in range(R):
            for c in range(Cn):
                k = K[r, c]
                p = np.abs(k) / np.linalg.norm(k)
                sq = Square(side_length=cs, stroke_width=0.6, stroke_color=BLACK, fill_opacity=1,
                            fill_color=rgb_to_color(np.clip([p[1], p[2], p[0]], 0, 1)))
                sq.move_to(org + np.array([(c + 0.5) * cs, (r + 0.5) * cs, 0]))
                grid.add(sq)
        gh = ZH("每个像素的 Pauli 伪彩色", 20, GREY_B).next_to(grid, UP, buff=0.12)
        gl = VGroup(ZH("本体：二面角", 20, C_EVEN).next_to(grid, DOWN, buff=0.12).align_to(grid, LEFT),
                    ZH("太阳翼：平板", 20, C_ODD).next_to(grid, DOWN, buff=0.12).align_to(grid, RIGHT))
        self.play(FadeIn(grid, lag_ratio=0.01), FadeIn(gh, gl), run_time=1.5)
        formula = MT(r"\mathbf T=\langle\mathbf k\,\mathbf k^H\rangle,\quad T_{ij}=\langle k_i k_j^*\rangle", 32)
        formula.move_to([-4.3, 2.35, 0])
        self.play(FadeIn(formula))

        # 右侧：T 的 |T_ij|/Span 热图 + 特征值条
        hm0 = np.array([1.2, 0.35, 0])
        hcs = 0.95

        def heat(T):
            span = np.real(np.trace(T))
            g = VGroup()
            for i in range(3):
                for j in range(3):
                    v = abs(T[i, j]) / span
                    sq = Square(side_length=hcs, stroke_width=1, stroke_color=GREY_C, fill_opacity=1,
                                fill_color=interpolate_color(BLACK, ORANGE, min(1, v / 0.8)))
                    sq.move_to(hm0 + np.array([(j - 1) * hcs, (1 - i) * hcs, 0]))
                    g.add(sq, MT(f"{v:.2f}", 24, WHITE).move_to(sq))
            return g

        def eig(T):
            span = np.real(np.trace(T))
            ev = np.sort(np.linalg.eigvalsh(T))[::-1] / span
            g = VGroup()
            b0 = np.array([4.55, -1.0, 0])
            for i, e in enumerate(ev):
                h = max(1e-3, 2.4 * max(e, 0))
                g.add(Rectangle(width=0.55, height=h, stroke_width=0, fill_color=TEAL, fill_opacity=0.9)
                      .move_to(b0 + RIGHT * 0.8 * i, aligned_edge=DOWN))
                g.add(MT(f"{max(e, 0):.2f}", 22).next_to(b0 + RIGHT * 0.8 * i + UP * h, UP, buff=0.06))
            return g

        hh = MT(r"|T_{ij}|/\mathrm{Span}", 26, GREY_A).next_to(hm0 + UP * 1.5 * hcs, UP, buff=0.12)
        rl = VGroup(*[MT(s, 24, c).next_to(hm0 + np.array([-1.5 * hcs, (1 - i) * hcs, 0]), LEFT, buff=0.1)
                      for i, (s, c) in enumerate([("1", C_ODD), ("2", C_EVEN), ("3", C_CROSS)])])
        b0 = np.array([4.55, -1.0, 0])
        eb = Line(b0 + LEFT * 0.4, b0 + RIGHT * 2.0, color=GREY_B)
        el = ZH("T 的特征值 / Span", 20, GREY_B).next_to(eb, DOWN, buff=0.12)
        el2 = MT(r"\lambda_1\ \ \lambda_2\ \ \lambda_3", 24, GREY_B).next_to(eb, UP, buff=2.95)

        win = Rectangle(width=cs, height=cs, color=YELLOW, stroke_width=5)

        def wpos(r0, c0, h, w):
            return org + np.array([(c0 + w / 2) * cs, (r0 + h / 2) * cs, 0])

        def Tof(r0, c0, h, w):
            ks = K[r0:r0 + h, c0:c0 + w].reshape(-1, 3)
            return sum(np.outer(k, k.conj()) for k in ks) / len(ks)

        win.move_to(wpos(2, 1, 1, 1))
        T = Tof(2, 1, 1, 1)
        H, E = heat(T), eig(T)
        cap.say("窗口只有 1 个像素时：T = k k^H 永远是秩 1，只有一个非零特征值")
        self.play(Create(win), FadeIn(H, hh, rl, eb, el, E))
        self.wait(3)
        win2 = Rectangle(width=3 * cs, height=3 * cs, color=YELLOW, stroke_width=5).move_to(wpos(1, 1, 3, 3))
        T = Tof(1, 1, 3, 3)
        cap.say("换成 3×3 窗口在本体区平均：仍以偶次散射 T₂₂ 为主，相关性降低")
        self.play(Transform(win, win2), Transform(H, heat(T)), Transform(E, eig(T)), run_time=1.2)
        self.wait(2.5)
        cap.say("窗口滑向本体与太阳翼的交界：两种机理混在一起，第二个特征值长出来")
        for c0 in range(2, 8):
            T = Tof(1, c0, 3, 3)
            self.play(win.animate.move_to(wpos(1, c0, 3, 3)), Transform(H, heat(T)), Transform(E, eig(T)),
                      run_time=0.9)
            if c0 in (3, 4):
                self.wait(1.4)
        cap.say("进入太阳翼区：T₁₁（奇次）占主导，又回到“一种机理”")
        self.wait(2.5)
        note = ZH("对角元 = 三种机理的平均功率；非对角元 = 相关性；迹 = Span", 22, YELLOW)
        cap.say("DB-SSIT 的 6 维特征（A–F）就是从这个 3×3 矩阵里读出来的")
        fit(note, 6.2).move_to([-3.4, -2.6, 0])
        self.play(FadeIn(note))
        self.wait(3)
