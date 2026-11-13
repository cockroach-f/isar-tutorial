"""第 2 章 · ISAR 成像：多普勒∝横向坐标、横向分辨率、MTRC、运动补偿。

几何约定与正文一致：雷达在上方，视线 LOS 沿 y 指向远离雷达的方向（画面向下）；
R_k = y_k cosθ + x_k sinθ，x_k>0 的点在转动中远离雷达（画面上顺时针转），f_d = -2ωx_k/λ < 0。
"""
from common import *

PT_COLORS = [BLUE_C, WHITE, RED_C]


def radar_icon(pos, size=0.35):
    tri = Triangle(color=WHITE, fill_opacity=1).scale(size).rotate(PI).move_to(pos)
    lab = ZH("雷达", 22).next_to(tri, RIGHT, buff=0.12)
    return VGroup(tri, lab)


def rot_screen(C, x, y, th, s=1.0):
    """物理 (x, y)（y 远离雷达）转过 th 后的画面坐标。"""
    xp = x * np.cos(th) - y * np.sin(th)
    yp = y * np.cos(th) + x * np.sin(th)
    return np.array([C[0] + s * xp, C[1] - s * yp, 0])


class M6_DopplerPhasor(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 6  转台模型：横向坐标不同的点，多普勒不同"))
        C = np.array([-3.7, -0.55, 0])
        radar = radar_icon([-3.7, 2.75, 0])
        los = Arrow([-3.7, 2.45, 0], [-3.7, 1.7, 0], buff=0, color=GREY_B, stroke_width=3)
        losl = MT(r"y", 26, GREY_B).next_to(los, LEFT, buff=0.1)
        disk = Circle(radius=2.0, color=ORANGE, stroke_width=2).move_to(C).set_stroke(opacity=0.7)
        disk.set_fill(ORANGE, opacity=0.05)
        pts = [(-1.5, 0.35), (0.0, -0.45), (1.5, -0.15)]
        th = ValueTracker(0.0)
        body = always_redraw(lambda: Line(rot_screen(C, -1.75, 0.1, th.get_value()),
                                          rot_screen(C, 1.75, -0.2, th.get_value()), color=GREY_D, stroke_width=10))
        dots = [always_redraw(lambda i=i: Dot(rot_screen(C, *pts[i], th.get_value()), radius=0.11, color=PT_COLORS[i]))
                for i in range(3)]
        xax = DashedLine(C + LEFT * 2.3, C + RIGHT * 2.3, color=GREY_C, stroke_width=1.5)
        xl = MT(r"x", 26, GREY_C).next_to(C + RIGHT * 2.3, RIGHT, buff=0.08)
        self.play(FadeIn(radar, los, losl), Create(disk), Create(xax), FadeIn(xl))
        self.add(body, *dots)
        cap.say("平动补偿后，目标绕中心转动；雷达沿视线 y 测距离")
        self.wait(1)

        def varrow(i):
            x, y = pts[i]
            t = th.get_value()
            p = rot_screen(C, x, y, t)
            v = (x * np.cos(t) - y * np.sin(t)) / 1.5 * 0.75   # 径向速度 ∝ x'
            if abs(v) < 0.06:
                return VGroup()
            return Arrow(p, p + DOWN * v, buff=0, color=PT_COLORS[i], stroke_width=5,
                         max_tip_length_to_length_ratio=0.35)

        arrs = [always_redraw(lambda i=i: varrow(i)) for i in range(3)]
        self.add(*arrs)
        cap.say("转动时各点的径向速度 v_k = x_k ω：右侧 x>0 远离雷达，左侧 x<0 靠近", size=24)
        self.play(th.animate.set_value(0.12), run_time=3, rate_func=linear)
        eq1 = MT(r"R_k\approx y_k + x_k\,\omega t_m", 32).move_to([-3.7, 1.95, 0]).shift(RIGHT * 0.0)
        eq1.next_to(los, RIGHT, buff=0.35)
        self.play(FadeIn(eq1))

        # ---------- 右：三个相量 ----------
        ys = [1.55, 0.25, -1.05]
        names = [r"x_k=-1.5\ \mathrm{m}", r"x_k=0", r"x_k=+1.5\ \mathrm{m}"]
        notes = ["靠近  f_d>0", "不动  f_d=0", "远离  f_d<0"]
        circs, phs, labs = VGroup(), [], VGroup()
        tt = ValueTracker(0.0)
        for i, y in enumerate(ys):
            cc = Circle(radius=0.48, color=GREY_B, stroke_width=2).move_to([0.9, y, 0])
            circs.add(cc)
            xk = pts[i][0]
            phs.append(always_redraw(lambda c=cc.get_center(), xk=xk, i=i: Arrow(
                c, c + 0.46 * np.array([np.cos(-2 * PI * 0.45 * xk / 1.5 * tt.get_value() + PI / 2),
                                        np.sin(-2 * PI * 0.45 * xk / 1.5 * tt.get_value() + PI / 2), 0]),
                buff=0, color=PT_COLORS[i], stroke_width=5, max_tip_length_to_length_ratio=0.3)))
            labs.add(VGroup(MT(names[i], 28, PT_COLORS[i]), ZH(notes[i], 22, GREY_A))
                     .arrange(DOWN, aligned_edge=LEFT, buff=0.08).next_to(cc, RIGHT, buff=0.35))
        hd = ZH("回波相位 φ = −4πR/λ 的“旋转箭头”", 22, GREY_B).move_to([2.6, 2.55, 0])
        self.play(FadeIn(hd), Create(circs), FadeIn(labs))
        self.add(*phs)
        cap.say("距离增大 → 相位减小 → 箭头顺时针转；|x_k| 越大转得越快")
        self.play(th.animate.set_value(0.30), tt.animate.set_value(4.5), run_time=6, rate_func=linear)
        eq2 = MT(r"f_{d,k}=-\frac{2}{\lambda}\frac{\mathrm dR_k}{\mathrm dt_m}\approx-\frac{2\omega}{\lambda}\,x_k",
                 34, YELLOW).move_to([3.5, -2.0, 0])
        box = SurroundingRectangle(eq2, color=YELLOW, buff=0.12)
        cap.say("箭头的转速就是多普勒频率：它正比于横向坐标 x_k（式 2.4）")
        self.play(Write(eq2), Create(box), th.animate.set_value(0.38), tt.animate.set_value(6.0),
                  run_time=2.5, rate_func=linear)
        self.play(th.animate.set_value(0.46), tt.animate.set_value(7.5), run_time=2, rate_func=linear)

        # ---------- 谱：慢时间 FFT ----------
        self.play(FadeOut(eq2, box, hd, eq1))
        ax = NumberLine(x_range=[-1.2, 1.2, 0.6], length=5.0, include_ticks=True, stroke_width=2).move_to([3.4, -2.35, 0])
        axl = MT(r"f_d", 28).next_to(ax, RIGHT, buff=0.12)
        zero = MT(r"0", 22, GREY_B).next_to(ax.n2p(0), DOWN, buff=0.1)
        self.play(Create(ax), FadeIn(axl, zero))
        spikes = VGroup()
        for i in range(3):
            fd = -pts[i][0] / 1.5
            base = ax.n2p(fd)
            spikes.add(Line(base, base + UP * 0.85, color=PT_COLORS[i], stroke_width=7))
        cap.say("对慢时间做 FFT：每个箭头变成频谱上的一根峰，频率轴就是横向坐标轴")
        self.play(*[TransformFromCopy(circs[i], spikes[i]) for i in range(3)], run_time=1.8)
        self.wait(1)
        cap.say("x 越大 → f_d 越负：频率轴与 x 轴方向相反（代码里用 ifft 把方向翻回来）")
        self.play(th.animate.set_value(0.55), tt.animate.set_value(9.0), run_time=3, rate_func=linear)
        self.wait(1)


class M7_CrossRangeRes(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 7  横向分辨率：转得越多，多普勒谱峰越窄"))
        lam, om, x1, x2 = 0.03, 0.05, 2.0, 2.15
        f1, f2 = -2 * om * x1 / lam, -2 * om * x2 / lam
        T = ValueTracker(0.6)
        # 左：积累转角扇形
        C = np.array([-4.6, 0.75, 0])
        disk = Circle(radius=1.3, color=GREY_B, stroke_width=2).move_to(C)
        radar = radar_icon([-4.6, 2.75, 0])
        wedge = always_redraw(lambda: AnnularSector(inner_radius=0, outer_radius=1.3, start_angle=PI / 2,
                                                    angle=-om * T.get_value() * 6, color=ORANGE,
                                                    fill_opacity=0.45).shift(C))
        wl = ZH("积累转角（放大 6 倍显示）", 20, GREY_B).next_to(disk, DOWN, buff=0.15)
        self.play(FadeIn(radar), Create(disk), FadeIn(wl))
        self.add(wedge)
        # 读数
        def rd():
            t = T.get_value()
            dth = om * t
            return VGroup(
                MT(rf"T={t:.2f}\ \mathrm{{s}}", 30),
                MT(rf"\Delta\theta=\omega T={np.degrees(dth):.2f}^\circ", 30),
                MT(rf"\rho_a=\frac{{\lambda}}{{2\Delta\theta}}={100 * lam / (2 * dth):.1f}\ \mathrm{{cm}}", 30, YELLOW),
            ).arrange(DOWN, aligned_edge=LEFT, buff=0.14).move_to([-4.5, -1.95, 0])
        read = always_redraw(rd)
        self.add(read)
        # 右：谱
        ax = Axes(x_range=[-9, -5, 0.5], y_range=[0, 1.1, 0.5], x_length=7.0, y_length=4.0, tips=False,
                  axis_config={"stroke_width": 2}).move_to([2.6, 0.35, 0])
        nums = VGroup(*[MT(str(v), 22, GREY_B).next_to(ax.c2p(v, 0), DOWN, buff=0.1) for v in (-9, -8, -7, -6, -5)])
        axl = MT(r"f_d\ /\ \mathrm{Hz}", 26).next_to(ax.c2p(-5, 0), DOWN, buff=0.45).shift(LEFT * 0.4)
        lines = VGroup(DashedLine(ax.c2p(f1, 0), ax.c2p(f1, 1.05), color=BLUE_C),
                       DashedLine(ax.c2p(f2, 0), ax.c2p(f2, 1.05), color=RED_C))
        ll = VGroup(MT(r"x=2.00\ \mathrm m", 22, BLUE_C).next_to(ax.c2p(f1, 1.05), UP, buff=0.05).shift(RIGHT * 0.45),
                    MT(r"x=2.15\ \mathrm m", 22, RED_C).next_to(ax.c2p(f2, 1.05), UP, buff=0.05).shift(LEFT * 0.45))
        self.play(Create(ax), FadeIn(nums, axl, lines, ll))
        fgrid = np.linspace(-9, -5, 600)

        def spec():
            t = T.get_value()
            s = np.sqrt(np.sinc(t * (fgrid - f1)) ** 2 + np.sinc(t * (fgrid - f2)) ** 2)  # 两点回波相位差 90°
            s = np.abs(s) / np.abs(s).max()
            return VMobject(color=ORANGE, stroke_width=4).set_points_smoothly(
                [ax.c2p(f, v) for f, v in zip(fgrid[::3], s[::3])])
        sp = always_redraw(spec)
        self.add(sp)
        cap.say("例题 2.3：两点横向相距 15 cm，多普勒只差 0.5 Hz；观测时间短时两峰融成一团")
        self.wait(2.5)
        cap.say("观测时间 T 越长，频率分辨率 1/T 越细，谱峰越窄", )
        self.play(T.animate.set_value(2.0), run_time=6, rate_func=linear)
        cap.say("T=2 s（转过 5.73°）时 1/T=0.5 Hz：两峰刚好分开，ρ_a=15 cm")
        self.wait(3)
        self.play(T.animate.set_value(4.0), run_time=4, rate_func=linear)
        eq = MT(r"\rho_a=\frac{\lambda}{2\omega}\cdot\frac{1}{T}=\frac{\lambda}{2\Delta\theta}", 36, YELLOW)
        eq.move_to([2.6, 2.75, 0])
        cap.say("横向分辨率只由波长和积累转角决定，与距离无关")
        self.play(FadeIn(eq))
        self.wait(3)


class M8_MTRC(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 8  越分辨单元走动（MTRC）：外侧的点会跨距离单元"))
        rho = 0.15
        xs = [0.5, 1.5, 3.0]
        cols = [GREEN_C, YELLOW, RED_C]
        th = ValueTracker(0.0)
        s = 0.95
        C = np.array([-4.3, 0.1, 0])
        radar = radar_icon([-4.3, 2.75, 0])
        bar = always_redraw(lambda: Line(rot_screen(C, -0.6, 0, th.get_value() * 4, s),
                                         rot_screen(C, 3.2, 0, th.get_value() * 4, s), color=GREY_D, stroke_width=10))
        dots = [always_redraw(lambda i=i: Dot(rot_screen(C, xs[i], 0, th.get_value() * 4, s), radius=0.11,
                                             color=cols[i])) for i in range(3)]
        cen = Dot(C, radius=0.07, color=WHITE)
        gl = ZH("转角放大 4 倍显示", 20, GREY_B).move_to([-4.3, -1.75, 0])
        self.play(FadeIn(radar, cen, gl))
        self.add(bar, *dots)
        xl = VGroup(*[MT(rf"x={x:g}\ \mathrm m", 22, c).next_to(rot_screen(C, x, 0, 0, s), [UP, DOWN][i % 2], buff=0.18)
                      for i, (x, c) in enumerate(zip(xs, cols))])
        self.play(FadeIn(xl))
        self.wait(1.2)
        self.play(FadeOut(xl), run_time=0.5)
        # 右：距离历程
        ax = Axes(x_range=[0, 0.1, 0.02], y_range=[-0.075, 0.375, 0.15], x_length=5.2, y_length=4.5, tips=False,
                  axis_config={"stroke_width": 2, "include_ticks": False}).move_to([2.0, 0.1, 0])
        bands = VGroup()
        for k in range(3):
            r = Rectangle(width=5.2, height=4.5 / 3, stroke_width=0,
                          fill_color=[GREY_E, BLACK][k % 2], fill_opacity=0.9)
            r.move_to(ax.c2p(0.05, k * rho))
            bands.add(r)
        bl = VGroup(*[ZH(f"距离单元 {k + 1}", 20, GREY_B).next_to(ax.c2p(0.1, k * rho), RIGHT, buff=0.12)
                      for k in range(3)])
        for b in bl:
            if b.get_right()[0] > 7.0:
                b.shift(LEFT * (b.get_right()[0] - 6.95))
        xlab = MT(r"\theta\ (\mathrm{rad})", 24).next_to(ax.c2p(0.1, -0.075), DOWN, buff=0.1).shift(LEFT * 0.4)
        xn = VGroup(*[MT(f"{v:.2f}", 20, GREY_B).next_to(ax.c2p(v, -0.075), DOWN, buff=0.08) for v in (0, 0.05)])
        ylab = MT(r"\Delta R=x\sin\theta", 26).next_to(ax.c2p(0, 0.375), UP, buff=0.12)
        self.play(FadeIn(bands), Create(ax), FadeIn(bl, xlab, xn, ylab))
        tr = [always_redraw(lambda i=i: ax.plot(lambda t: xs[i] * np.sin(t), x_range=[0, max(1e-4, th.get_value())],
                                                color=cols[i], stroke_width=4)) for i in range(3)]
        hd = [always_redraw(lambda i=i: Dot(ax.c2p(th.get_value(), xs[i] * np.sin(th.get_value())), color=cols[i],
                                            radius=0.07)) for i in range(3)]
        self.add(*tr, *hd)
        cap.say("RD 算法假设：积累期间每个点都待在同一个距离单元（ρ_r = 15 cm）")
        self.play(th.animate.set_value(0.05), run_time=5, rate_func=linear)
        cap.say("距离变化量 ≈ |x|Δθ：离转动中心越远，走得越多")
        self.play(th.animate.set_value(0.1), run_time=5, rate_func=linear)
        ann = VGroup(
            MT(r"0.5\times0.1=0.05\ \mathrm m<\rho_r", 24, GREEN_C),
            MT(r"1.5\times0.1=0.15\ \mathrm m=\rho_r", 24, YELLOW),
            MT(r"3\times0.1=0.30\ \mathrm m=2\rho_r", 24, RED_C),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12).move_to([1.4, 1.55, 0])
        bg = BackgroundRectangle(ann, fill_opacity=0.8, buff=0.1)
        cap.say("例题 2.5：Δθ = 0.1 rad 时，x = 3 m 的点走过约 2 个距离单元 → 弧形拖尾")
        self.play(FadeIn(bg, ann))
        self.wait(3)
        crit = MT(r"|x|_{\max}\,\Delta\theta<\rho_r\ \Longleftrightarrow\ |x|_{\max}<\frac{\rho_r}{\Delta\theta}=1.5\ \mathrm m",
                  32, YELLOW)
        crit.move_to([0, -2.85, 0])
        cbg = BackgroundRectangle(crit, fill_opacity=0.9, buff=0.1)
        cap.say("经验判据：目标横向半尺寸小于 ρ_r/Δθ 时，RD 算法可以放心使用")
        self.play(FadeIn(cbg, crit))
        self.wait(3.5)


class M9_MotionComp(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 9  运动补偿两步走：包络对齐 + 初相校正"))
        Np, Nr = 16, 34
        cw, chh = 0.18, 0.17
        org = np.array([-6.3, -2.4, 0])          # 左下角
        cells = [6, 10, 13]
        amps = [1.0, 0.7, 0.85]
        shift_per = 0.67                         # 每个脉冲平移 0.1 m = 0.67 个距离单元（例题 2.6 的比例）
        frame = Rectangle(width=Nr * cw, height=Np * chh, color=GREY_B, stroke_width=1.5)
        frame.move_to(org + np.array([Nr * cw / 2, Np * chh / 2, 0]))
        xlab = ZH("距离单元 →", 20, GREY_B).next_to(frame, DOWN, buff=0.1)
        ylab = ZH("脉冲 →", 20, GREY_B).rotate(PI / 2).next_to(frame, LEFT, buff=0.1)
        hd = ZH("HRRP 历程", 22, GREY_A).next_to(frame, UP, buff=0.1)
        self.play(Create(frame), FadeIn(xlab, ylab, hd))
        rows = VGroup()
        for m in range(Np):
            row = VGroup()
            for c, a in zip(cells, amps):
                pos = c + shift_per * m
                r = Rectangle(width=cw * 1.6, height=chh * 0.9, stroke_width=0,
                              fill_color=interpolate_color(BLUE_E, YELLOW, a), fill_opacity=1)
                r.move_to(org + np.array([(pos + 0.5) * cw, (m + 0.5) * chh, 0]))
                row.add(r)
            rows.add(row)
        cap.say("目标平动：例题 2.6 中每个脉冲平移 0.1 m，HRRP 历程变成斜线")
        self.play(LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.15), run_time=3)
        self.wait(1)
        cap.say("第 1 步 包络对齐：把每条 HRRP 平移回去，让同一散射点落在同一距离单元")
        self.play(*[rows[m].animate.shift(LEFT * shift_per * m * cw) for m in range(Np)], run_time=3)
        self.wait(1)
        col = SurroundingRectangle(VGroup(*[rows[m][0] for m in range(Np)]), color=ORANGE, buff=0.03)
        self.play(Create(col))

        # 右：该距离单元逐脉冲相位
        rng = np.random.default_rng(3)
        err = rng.uniform(-np.pi, np.pi, Np)     # 残余平动相位（包络对齐只到厘米级 → 相位仍乱）
        dop = 2 * np.pi * 0.09 * np.arange(Np)  # 转动带来的线性相位（有用信息）
        lam = ValueTracker(1.0)                  # 1：有误差；0：校正后
        cx = np.linspace(0.6, 6.4, 8)
        cy = [1.55, 0.45]
        centers = [np.array([cx[m % 8], cy[m // 8], 0]) for m in range(Np)]
        circ = VGroup(*[Circle(radius=0.3, color=GREY_D, stroke_width=1.5).move_to(c) for c in centers])

        def ph():
            g = VGroup()
            for m in range(Np):
                a = dop[m] + lam.get_value() * err[m]
                g.add(Arrow(centers[m], centers[m] + 0.29 * np.array([np.cos(a), np.sin(a), 0]), buff=0,
                            color=ORANGE, stroke_width=4, max_tip_length_to_length_ratio=0.35))
            return g
        arr = always_redraw(ph)
        phd = ZH("橙框距离单元在 16 个脉冲上的回波相位", 22, GREY_A).move_to([3.5, 2.45, 0])
        self.play(FadeIn(phd), Create(circ))
        self.add(arr)
        # 谱
        ax = Axes(x_range=[0, 1, 0.25], y_range=[0, 1.05, 0.5], x_length=5.6, y_length=1.6, tips=False,
                  axis_config={"stroke_width": 2, "include_ticks": False}).move_to([3.5, -1.55, 0])
        axl = ZH("方位谱（慢时间 FFT）", 20, GREY_B).next_to(ax, DOWN, buff=0.08)

        def spec():
            a = dop + lam.get_value() * err
            S = np.abs(np.fft.fft(np.exp(1j * a), 256))
            S = S / Np
            fx = np.arange(256) / 256
            return VMobject(color=YELLOW, stroke_width=3).set_points_as_corners(
                [ax.c2p(f, v) for f, v in zip(fx, S)])
        sp = always_redraw(spec)
        self.play(Create(ax), FadeIn(axl))
        self.add(sp)
        cap.say("包络对齐到 1 cm 以内，残余相位误差仍有约 4.2 rad：相位杂乱，谱峰散开")
        self.wait(3.5)
        cap.say("第 2 步 初相校正 / 自聚焦：消去各脉冲共有的平动相位，只留下转动带来的线性相位")
        self.play(lam.animate.set_value(0.0), run_time=4)
        cap.say("相位整齐地匀速旋转 → 方位谱聚成一根尖峰，这个散射点就“聚焦”了")
        self.wait(3.5)
