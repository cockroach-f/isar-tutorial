"""ISAR 教程 manim 动画的公共工具（Manim Community v0.22）。

中文用 Text（Noto Sans CJK SC），公式用 MathTex（LaTeX），两者不混排。
渲染：tools/render_manim.sh（720p30 → 再压缩到 docs/videos/，封面到 docs/figures/video_frames/）。
"""
from manim import *  # noqa: F401,F403
import numpy as np

FONT = "Noto Sans CJK SC"
C_ODD = BLUE_C     # 奇次散射（Pauli B 通道）
C_EVEN = RED_C     # 偶次散射（Pauli R 通道）
C_CROSS = GREEN_C  # 交叉极化（Pauli G 通道）
C_HL = YELLOW


def ZH(s, size=26, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def MT(s, size=34, color=WHITE, **kw):
    return MathTex(s, font_size=size, color=color, **kw)


def fit(m, w=13.2):
    if m.width > w:
        m.scale_to_fit_width(w)
    return m


def title(s, size=32):
    return fit(ZH(s, size, weight=BOLD)).to_edge(UP, buff=0.28)


class Cap:
    """底部字幕：一行中文（可选附一个公式），自动居中、限宽。"""

    def __init__(self, scene, y=-3.55):
        self.scene, self.y, self.cur = scene, y, None

    def build(self, s, math=None, size=24):
        parts = [ZH(s, size)]
        if math is not None:
            parts.append(MT(math, size + 4))
        g = VGroup(*parts).arrange(RIGHT, buff=0.18)
        fit(g, 13.0).move_to([0, self.y, 0])
        bg = BackgroundRectangle(g, color=BLACK, fill_opacity=0.85, buff=0.12)
        return VGroup(bg, g)

    def say(self, s, math=None, size=24, run_time=0.5):
        new = self.build(s, math, size)
        if self.cur is None:
            self.scene.play(FadeIn(new), run_time=run_time)
        else:
            self.scene.play(FadeOut(self.cur), FadeIn(new), run_time=run_time)
        self.cur = new
        return new
