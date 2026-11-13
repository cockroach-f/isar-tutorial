"""第 12 章 MLFR · 多站 ISAR：同一目标在不同站看起来“姿态、尺度”不同，先对齐再融合。"""
from common import *

SAT = ([(x, y) for x in np.linspace(-0.35, 0.35, 3) for y in np.linspace(-0.45, 0.45, 4)]
       + [(x, y) for x in np.linspace(-1.6, -0.6, 6) for y in (-0.15, 0.15)]
       + [(x, y) for x in np.linspace(0.6, 1.6, 6) for y in (-0.15, 0.15)]
       + [(0.0, 0.75), (0.0, 1.05)])
SAT = np.array(SAT)
COLS = [BLUE_C, GREEN_C, ORANGE]


def R2(a):
    return np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])


class M14_Multistatic(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 14  多站 ISAR：同一目标，三个站看到三幅“不一样”的像"))
        C = np.array([-3.6, -0.75, 0])
        Rr = 2.55
        ang = [PI / 2, PI / 2 + 0.75, PI / 2 - 0.75]      # 三个站的方位
        th = ValueTracker(0.0)
        tgt = always_redraw(lambda: VGroup(*[Dot(C + 0.62 * np.array([*(R2(th.get_value()) @ p), 0]), radius=0.045,
                                                 color=WHITE) for p in SAT]))
        rads = VGroup()
        for k, a in enumerate(ang):
            pos = C + Rr * np.array([np.cos(a), np.sin(a), 0])
            tri = Triangle(color=COLS[k], fill_opacity=1).scale(0.2).rotate(a + PI / 2).move_to(pos)
            ln = DashedLine(pos, C, color=COLS[k], stroke_width=2).set_opacity(0.6)
            lab = ZH(f"站 {k + 1}", 20, COLS[k]).next_to(tri, [UP, LEFT, RIGHT][k], buff=0.1)
            rads.add(VGroup(ln, tri, lab))
        self.play(FadeIn(rads, lag_ratio=0.3))
        self.add(tgt)
        cap.say("三个雷达站同时观测同一颗卫星，视线方向各不相同")
        self.play(th.animate.set_value(0.25), run_time=2.5, rate_func=linear)

        # 右：三个站的 ISAR 像（站坐标：横向 × 距离）
        scale = [1.0, 0.8, 1.2]   # 不同带宽 / 积累角 → 尺度不同
        cen = [np.array([1.35 + 2.1 * k, 0.75, 0]) for k in range(3)]
        panels = VGroup()
        for k in range(3):
            sq = Square(side_length=1.95, stroke_color=COLS[k], stroke_width=2, fill_color=BLACK, fill_opacity=1)
            sq.move_to(cen[k])
            lab = ZH(f"站 {k + 1} 的像", 20, COLS[k]).next_to(sq, UP, buff=0.1)
            panels.add(VGroup(sq, lab))
        al = ValueTracker(0.0)    # 0：原始；1：对齐后

        def img(k):
            a = ang[k] - PI / 2       # 站视线相对站 1 的转角
            t = th.get_value()
            g = VGroup()
            for p in SAT:
                q = R2(t - a * (1 - al.get_value())) @ p
                s = scale[k] + (1 - scale[k]) * al.get_value()
                q = q * np.array([s, 1 / s ** 0.3])
                g.add(Dot(cen[k] + 0.4 * np.array([*q, 0]), radius=0.04, color=interpolate_color(YELLOW, WHITE, 0.3)))
            return g
        imgs = [always_redraw(lambda k=k: img(k)) for k in range(3)]
        self.play(FadeIn(panels))
        self.add(*imgs)
        cap.say("每个站的像都是目标在“自己视线坐标系”里的投影：方向不同")
        self.play(th.animate.set_value(0.65), run_time=4, rate_func=linear)
        cap.say("各站带宽、积累角也可能不同 → 横向尺度不同（类内差异大）")
        self.wait(2.5)
        warn = ZH("直接拼接融合：43.3% 的实验反而不如最好的单站", 22, RED_C)
        fit(warn, 6.3).move_to([3.45, -1.0, 0])
        self.play(FadeIn(warn))
        self.wait(2.5)
        self.play(FadeOut(warn))
        amfa = VGroup(ZH("AMFA：每站学 5 个参数", 22, YELLOW),
                      MT(r"T=T_{Sc}\,T_{Rt}\,T_{Tr}", 30, YELLOW),
                      ZH("缩放 2 + 旋转 1 + 平移 2", 20, GREY_A)).arrange(DOWN, buff=0.12).move_to([3.45, -1.25, 0])
        cap.say("MLFR 先对齐：对各站特征图做仿射变换，摆到统一的姿态和尺度")
        self.play(FadeIn(amfa))
        self.play(al.animate.set_value(1.0), run_time=3.5)
        self.wait(1)
        cap.say("对齐之后再用 Transformer 做站间重建、互相补充：先对齐，后融合")
        self.play(th.animate.set_value(1.0), run_time=3.5, rate_func=linear)
        self.wait(2)
