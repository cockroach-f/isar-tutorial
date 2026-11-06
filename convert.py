#!/usr/bin/env python3
"""Convert Pandoc-flavored chapters_v2 markdown to MkDocs Material."""
from __future__ import annotations

import re
from pathlib import Path

SRC = Path("/workspace/isar-tutorial/chapters_v2")
DST = Path("/workspace/isar-pages/docs")

# source file -> (relative dest under docs/, nav title)
MAP = {
    "00_front.md": ("index.md", "前言"),
    "A0_math.md": ("part-a/A0_math.md", "第 0 章 数学与信号准备"),
    "A1_radar.md": ("part-a/A1_radar.md", "第 1 章 雷达基础"),
    "A2_isar.md": ("part-a/A2_isar.md", "第 2 章 ISAR 成像"),
    "A3_pol.md": ("part-a/A3_pol.md", "第 3 章 雷达极化"),
    "A4_hard.md": ("part-a/A4_hard.md", "第 4 章 识别难点"),
    "A5_dl.md": ("part-a/A5_dl.md", "第 5 章 深度学习入门（上）"),
    "A6_dl2.md": ("part-a/A6_dl2.md", "第 6 章 深度学习入门（下）"),
    "B1_dbssit.md": ("part-b/B1_dbssit.md", "第 7 章 DB-SSIT"),
    "B2_cvgnn.md": ("part-b/B2_cvgnn.md", "第 8 章 CV-GNN"),
    "B3_msn.md": ("part-b/B3_msn.md", "第 9 章 MSN"),
    "B4_cvpgt.md": ("part-b/B4_cvpgt.md", "第 10 章 CvPGT"),
    "B5_remi.md": ("part-b/B5_remi.md", "第 11 章 REMI"),
    "B6_mlfr.md": ("part-b/B6_mlfr.md", "第 12 章 MLFR"),
    "B7_dcanet.md": ("part-b/B7_dcanet.md", "第 13 章 DCA-Net"),
    "C1_synthesis.md": ("part-c/C1_synthesis.md", "第 14 章 横向对比"),
    "C2_projects.md": ("part-c/C2_projects.md", "第 15 章 阅读路线与入门项目"),
    "C3_glossary.md": ("part-c/C3_glossary.md", "第 16 章 术语表"),
    "D_appendix.md": ("appendix.md", "附录"),
}

BOX_TITLES = {
    "goal": ("tip", "本章目标"),
    "intuit": ("info", "直觉"),
    "key": ("success", "关键公式"),
    "example": ("example", "例题"),
    "pitfall": ("warning", "易错点"),
    "link": ("note", "基础回链"),
    "recap": ("summary", "小结"),
    "note": ("note", "说明"),
}

# Match opening fences like ::: {.box .goal} or ::: {.backref} or ::: {.video-block}
OPEN_RE = re.compile(
    r"^:::\s*\{\s*\.?(?P<body>[^}]+)\}\s*$"
)
# bare ::: close
CLOSE_RE = re.compile(r"^:::\s*$")

# image: ![alt](path){attrs}
IMG_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<path>[^)]+)\)(?:\{(?P<attrs>[^}]*)\})?"
)

# heading attrs {.unnumbered .part}
HEAD_ATTR_RE = re.compile(r"\s*\{[^}]*\}\s*$")

# YAML front matter
YAML_RE = re.compile(r"^---\n.*?\n---\n", re.S)

PAPER_FIG_NOTE = (
    '*（请对照原文 {fig}——因版权未在站点上转载期刊原图）*\n\n'
    '**{caption}**'
)


def parse_classes(body: str) -> list[str]:
    # body like ".box .goal" or "box .goal" or ".backref"
    parts = re.split(r"\s+", body.strip())
    classes = []
    for p in parts:
        p = p.lstrip(".")
        if p:
            classes.append(p)
    return classes


def indent_block(text: str) -> str:
    """Indent every line by 4 spaces for Material admonition body.
    Preserve blank lines as blank (still indented empty? Material wants 4-space indent on content).
    """
    lines = text.split("\n")
    out = []
    for line in lines:
        if line.strip() == "":
            out.append("")
        else:
            out.append("    " + line)
    return "\n".join(out).rstrip() + "\n"


def convert_images(text: str, depth: int) -> tuple[str, int]:
    """Rewrite image paths; replace paper_figs with copyright note.
    depth: how many dirs deep under docs/ (0 for index.md, 1 for part-a/...).
    Returns (new_text, n_paper_omitted).
    """
    prefix = "../" * depth
    omitted = 0

    def repl(m: re.Match) -> str:
        nonlocal omitted
        alt = m.group("alt")
        path = m.group("path").strip()
        # paper_figs → copyright note
        if path.startswith("paper_figs/") or "/paper_figs/" in path:
            omitted += 1
            # try extract "原文 Fig. N" from alt
            fig_m = re.search(r"(原文\s*Fig\.?\s*[\w.\-]+)", alt)
            fig = fig_m.group(1) if fig_m else "原文对应图"
            # caption is the whole alt
            return PAPER_FIG_NOTE.format(fig=fig, caption=alt)

        # figures/ videos/ code/ — relative from page
        if path.startswith(("figures/", "videos/", "code/")):
            new_path = prefix + path
        elif path.startswith("../"):
            new_path = path
        else:
            new_path = path

        # strip pandoc attrs; keep plain markdown image
        return f"![{alt}]({new_path})"

    return IMG_RE.sub(repl, text), omitted


def fix_video_html(text: str, depth: int) -> str:
    """Fix poster/src paths inside <video> tags."""
    prefix = "../" * depth

    def fix_attr(m: re.Match) -> str:
        attr, path = m.group(1), m.group(2)
        if path.startswith(("figures/", "videos/")):
            path = prefix + path
        return f'{attr}="{path}"'

    text = re.sub(
        r'(poster|src)="((?:figures|videos)/[^"]+)"',
        fix_attr,
        text,
    )
    return text


def convert_divs(text: str) -> str:
    """Convert Pandoc fenced divs to Material admonitions / raw HTML."""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        m = OPEN_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        classes = parse_classes(m.group("body"))
        # collect body until closing :::
        i += 1
        body_lines: list[str] = []
        while i < n and not CLOSE_RE.match(lines[i]):
            body_lines.append(lines[i])
            i += 1
        if i < n and CLOSE_RE.match(lines[i]):
            i += 1  # consume closing :::
        body = "\n".join(body_lines).strip("\n")

        if "video-block" in classes:
            # keep inner HTML as-is (paths fixed later); drop the fence
            out.append("")
            out.extend(body_lines)
            out.append("")
            continue

        if "backref" in classes:
            kind, title = "note", "基础回链"
        elif "box" in classes:
            # find the type class
            kind, title = "note", "说明"
            for c in classes:
                if c in BOX_TITLES:
                    kind, title = BOX_TITLES[c]
                    break
        else:
            # unknown div → note
            kind, title = "note", "说明"

        out.append(f'!!! {kind} "{title}"')
        out.append("")
        if body.strip():
            out.append(indent_block(body).rstrip("\n"))
        else:
            out.append("    ")
        out.append("")

    return "\n".join(out)


def strip_heading_attrs(text: str) -> str:
    out_lines = []
    for line in text.split("\n"):
        if line.startswith("#"):
            line = HEAD_ATTR_RE.sub("", line)
        out_lines.append(line)
    return "\n".join(out_lines)


def drop_part_heading(text: str) -> str:
    """Remove standalone '# Part X ...' lines (nav sections cover this)."""
    lines = text.split("\n")
    out = []
    for line in lines:
        if re.match(r"^#\s+Part\s+[ABC]\b", line):
            continue
        out.append(line)
    return "\n".join(out)


def demote_code_heading(text: str) -> str:
    """A2 has a mistaken H1 for a code excerpt — demote to H2."""
    return re.sub(
        r"^# (code/isar_core\.py[^\n]*)",
        r"## \1",
        text,
        flags=re.M,
    )


def convert_file(src_name: str, dest_rel: str) -> dict:
    src = SRC / src_name
    raw = src.read_text(encoding="utf-8")
    # strip YAML front matter
    raw = YAML_RE.sub("", raw)
    raw = strip_heading_attrs(raw)
    raw = drop_part_heading(raw)
    raw = demote_code_heading(raw)
    raw = convert_divs(raw)

    depth = dest_rel.count("/")  # index.md -> 0, part-a/x.md -> 1
    raw, omitted = convert_images(raw, depth)
    raw = fix_video_html(raw, depth)

    # tidy: collapse 3+ blank lines to 2
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    raw = raw.strip() + "\n"

    dest = DST / dest_rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(raw, encoding="utf-8")
    return {"src": src_name, "dest": dest_rel, "paper_figs_omitted": omitted, "chars": len(raw)}


def main():
    stats = []
    total_omit = 0
    for src_name, (dest_rel, _title) in MAP.items():
        s = convert_file(src_name, dest_rel)
        stats.append(s)
        total_omit += s["paper_figs_omitted"]
        print(f"OK  {src_name:20s} -> {dest_rel:30s}  omit_paper={s['paper_figs_omitted']}")
    print(f"\nTotal paper_figs omitted: {total_omit}")

    # write a short videos page
    videos_md = '''# 动画视频

本教程配套 4 段短动画（每段约 24–38 秒）。章节正文里也嵌了同一批视频。

## V1 转台 → 多普勒 → ISAR 像

<video controls preload="metadata" width="100%" poster="../figures/video_frames/V1_turntable_to_isar_2.png">
<source src="../videos/V1_turntable_to_isar.mp4" type="video/mp4">
</video>

左：目标转动；中：HRRP 历程；右：RD 像随积累转角变清晰。对应第 2 章。

## V2 脉冲压缩

<video controls preload="metadata" width="100%" poster="../figures/video_frames/V2_pulse_compression_2.png">
<source src="../videos/V2_pulse_compression.mp4" type="video/mp4">
</video>

匹配滤波滑动相关与带宽扫频。对应第 1 章。

## V3 少样本 episode

<video controls preload="metadata" width="100%" poster="../figures/video_frames/V3_fewshot_episode_2.png">
<source src="../videos/V3_fewshot_episode.mp4" type="video/mp4">
</video>

N-way K-shot 支撑集与查询集示意。对应第 6 章与少样本论文。

## V4 散焦

<video controls preload="metadata" width="100%" poster="../figures/video_frames/V4_defocus_2.png">
<source src="../videos/V4_defocus.mp4" type="video/mp4">
</video>

匀速 / 加速运动下多普勒展宽与散焦。对应第 2 章、CV-GNN。
'''
    (DST / "videos.md").write_text(videos_md, encoding="utf-8")
    print("OK  videos.md")


if __name__ == "__main__":
    main()
