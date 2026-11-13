"""第 1 章 · 匹配滤波把 LFM 各频率分量的相位拉齐（对应 1.4.3 节式 (1.10)–(1.13)）。"""
from common import *


class M5_ChirpPhasors(Scene):
    def construct(self):
        cap = Cap(self)
        self.add(title("动画 5  匹配滤波：把 LFM 各频率分量“拉齐”成一个尖峰"))

        # ---------- 左：时频图 ----------
        tf = Axes(x_range=[-1.2, 1.2, 0.5], y_range=[-0.7, 0.7, 0.5], x_length=5.2, y_length=3.6,
                  tips=False, axis_config={"include_ticks": False, "stroke_width": 2}).move_to([-3.9, 0.55, 0])
        tl = MT(r"t", 28).next_to(tf.x_axis, RIGHT, buff=0.1)
        fl = MT(r"f", 28).next_to(tf.y_axis, UP, buff=0.08)
        bB = MT(r"+B/2", 24, GREY_B).next_to(tf.c2p(0, 0.5), LEFT, buff=0.15)
        bmB = MT(r"-B/2", 24, GREY_B).next_to(tf.c2p(0, -0.5), LEFT, buff=0.15)
        hd = ZH("时频图", 24, GREY_B).next_to(tf, UP, buff=0.05)
        self.play(Create(tf), FadeIn(tl, fl, hd))
        echo = tf.plot(lambda t: t / 2, x_range=[-1, 1], color=YELLOW, stroke_width=5)
        el = MT(r"f(t)=K(t-\tau)", 26, YELLOW).next_to(tf.c2p(0.95, 0.55), UP, buff=0.05).shift(LEFT * 0.6)
        cap.say("回波 LFM：频率随时间线性上升，低频先到、高频后到，能量摊在整个脉宽里")
        self.play(Create(echo), FadeIn(el, bB, bmB), run_time=1.5)
        self.wait(1.2)
        # 频率分量“小段”沿 t 分布
        fs = np.linspace(-0.45, 0.45, 10)
        dots = VGroup(*[Dot(tf.c2p(2 * f, f), radius=0.06, color=interpolate_color(BLUE, RED, (f + 0.5))) for f in fs])
        self.play(FadeIn(dots, lag_ratio=0.1))
        cap.say("匹配滤波 H(f)=U*(f)：每个频率再补一个相反的时延，高频少等、低频多等")
        filt = tf.plot(lambda t: -t / 2, x_range=[-1, 1], color=TEAL, stroke_width=3)
        filt.set_stroke(opacity=0.8)
        flab = MT(r"h(t)=u^*(-t)", 26, TEAL).next_to(tf.c2p(-0.95, 0.55), UP, buff=0.05).shift(RIGHT * 0.5)
        self.play(Create(filt), FadeIn(flab))
        self.wait(0.6)
        self.play(*[d.animate.move_to(tf.c2p(0, f)) for d, f in zip(dots, fs)], run_time=2)
        vline = Line(tf.c2p(0, -0.5), tf.c2p(0, 0.5), color=ORANGE, stroke_width=6)
        self.play(Create(vline), FadeOut(echo, filt, el, flab))
        tau = MT(r"t=\tau", 26, ORANGE).next_to(tf.c2p(0, -0.55), DOWN, buff=0.08).shift(RIGHT * 0.45)
        self.play(FadeIn(tau))
        cap.say("所有频率分量在同一时刻 t=τ 到达：长脉冲被“压”成一根竖线", size=24)
        self.wait(1.5)

        # ---------- 右：相量叠加 ----------
        N = 10
        fn = (np.arange(N) + 0.5) / N - 0.5          # f_n / B
        cols = [interpolate_color(BLUE, RED, f + 0.5) for f in fn]
        u = ValueTracker(-2.6)                        # u = B (t - tau)
        L = 0.27
        org = np.array([2.65, 1.35, 0])

        def chain():
            g = VGroup()
            p = org.copy()
            for f, c in zip(fn, cols):
                ph = 2 * np.pi * f * u.get_value()
                q = p + L * np.array([np.cos(ph), np.sin(ph), 0])
                g.add(Line(p, q, color=c, stroke_width=5))
                p = q
            g.add(Arrow(org, p, buff=0, color=WHITE, stroke_width=4, max_tip_length_to_length_ratio=0.12))
            return g

        ch = always_redraw(chain)
        sumlab = ZH("10 个频率分量的相量首尾相接", 22, GREY_B).move_to([4.0, 2.75, 0])
        ax = Axes(x_range=[-3, 3, 1], y_range=[-0.3, 1.05, 0.5], x_length=6.0, y_length=2.4, tips=False,
                  axis_config={"stroke_width": 2, "include_ticks": True}).move_to([3.7, -1.65, 0])
        axl = MT(r"B(t-\tau)", 24).next_to(ax.c2p(2.5, -0.3), DOWN, buff=0.05)
        nums = VGroup(*[MT(f"{k:+d}" if k else "0", 22, GREY_B).next_to(ax.c2p(k, -0.3), DOWN, buff=0.05) for k in (-1, 1)])
        ylab = MT(r"y(t)", 24).next_to(ax.c2p(-3, 1.0), RIGHT, buff=0.1)

        def D(x):
            if abs(x) < 1e-9:
                return 1.0
            return np.sin(np.pi * x) / (N * np.sin(np.pi * x / N))

        trace = always_redraw(lambda: ax.plot(D, x_range=[-2.6, max(-2.59, u.get_value())], color=ORANGE,
                                              stroke_width=4))
        cursor = always_redraw(lambda: Dot(ax.c2p(u.get_value(), D(u.get_value())), color=WHITE, radius=0.06))
        self.play(FadeIn(sumlab), Create(ax), FadeIn(axl, nums, ylab))
        self.add(ch, trace, cursor)
        cap.say("每个频率分量是一个旋转箭头，转速正比于频率；输出 y(t) 是它们的和")
        self.play(u.animate.set_value(-1.0), run_time=4, rate_func=linear)
        cap.say("t 离 τ 较远时，箭头方向各不相同，首尾相接绕成圈，和很小")
        self.play(u.animate.set_value(0.0), run_time=3.5, rate_func=linear)
        eq = MT(r"Y(f)=\sigma\,|U(f)|^2 e^{-j2\pi f\tau}", 30, YELLOW).move_to([4.0, 0.25, 0])
        cap.say("t=τ：各分量相位全部拉齐，同相叠加形成尖峰（式 1.10）")
        self.play(FadeIn(eq))
        self.wait(2)
        self.play(FadeOut(eq))
        cap.say("t-τ=±1/B 时箭头恰好绕成一整圈，和为零：这就是 sinc 的第一个零点")
        self.play(u.animate.set_value(1.0), run_time=3, rate_func=linear)
        z1 = DashedLine(ax.c2p(1, -0.3), ax.c2p(1, 1.0), color=GREY_B)
        z0 = DashedLine(ax.c2p(-1, -0.3), ax.c2p(-1, 1.0), color=GREY_B)
        self.play(Create(z0), Create(z1))
        self.wait(1.5)
        self.play(u.animate.set_value(2.6), run_time=3, rate_func=linear)
        res = MT(r"\Delta t\approx \frac{1}{B}\ \Rightarrow\ \rho_r=\frac{c}{2B}", 34, YELLOW).move_to([4.0, 0.25, 0])
        cap.say("主瓣宽度只由带宽决定，与脉宽无关；长脉冲的能量全部集中到峰上")
        self.play(FadeIn(res))
        self.wait(3)
