import os
"""从论文 PDF 中按图注(Fig./Figure N)自动裁剪原文插图。用法: python extract_paper_figs.py
输出: ../paper_figs/<paper>_fig<N>.png
启发式: 找到图注块, 判定其所在栏, 向上搜索最近的正文段落(长文本块)作为上边界。"""
import fitz, re, os, sys
SRC = os.environ.get('ISAR_PAPERS_DIR', 'papers')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'paper_figs')
os.makedirs(OUT, exist_ok=True)
PAPERS = {'p1_DBSSIT':'01M68FJ1SEYH802Y8V3ZW4VWNC.pdf','p2_CVGNN':'01M68FJ1R3GHZ8V9GSG40HVVH8.pdf',
          'p3_MSN':'01M68FJ1RD5ZHWJEQ2776FHSCW.pdf','p4_CvPGT':'01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf',
          'p5_REMI':'01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p6_MLFR':'01M68FJ1QVRQND1JJGRHNQV3JD.pdf',
          'p7_DCANet':'01M68FJ1RFCZKVMD8JS4M43190.pdf'}
cap_re = re.compile(r'^(Fig\.|Figure)\s*(\d+)')
tab_re = re.compile(r'^(TABLE|Table)\s+[IVX\d]+')
def is_body(t, b):
    # 正文段落, 或者其它图注/表注 都作为上边界
    return (len(t) > 160) or cap_re.match(t) or tab_re.match(t)
for key, fn in PAPERS.items():
    d = fitz.open(os.path.join(SRC, fn)); done=set()
    for pi, p in enumerate(d):
        W, H = p.rect.width, p.rect.height
        blocks = [b for b in p.get_text('blocks') if b[6] == 0]
        for b in blocks:
            t = b[4].strip().replace('\n', ' ')
            m = cap_re.match(t)
            if not m: continue
            n = int(m.group(2))
            if n in done: continue
            x0, y0, x1, y1 = b[:4]
            wide = (x1 - x0) > W * 0.5 or (x0 < W*0.45 and x1 > W*0.55)
            if wide: cx0, cx1 = 0, W
            elif x1 <= W/2 + 10: cx0, cx1 = 0, W/2
            else: cx0, cx1 = W/2, W
            # 上边界: 本栏内图注上方最近的正文段落底部 / 页眉
            top = 40
            for bb in blocks:
                tt = bb[4].strip()
                if bb[3] <= y0 - 2 and bb[2] > cx0 + 5 and bb[0] < cx1 - 5 and is_body(tt, bb):
                    top = max(top, bb[3])
            if y0 - top < 40:   # 图在图注下方(少见)或失败
                continue
            # 若图跨栏(图形元素超出栏宽), 扩展到全宽
            gx0, gx1 = cx0, cx1
            for r in [x['rect'] for x in p.get_drawings()] + [p.get_image_bbox(im) for im in p.get_images(full=True) if True]:
                try:
                    if r.y0 >= top - 2 and r.y1 <= y0 + 2 and r.x0 < cx1 - 2 and r.x1 > cx0 + 2 and r.x0 >= cx0 - 30 and r.width > 5:
                        gx0 = min(gx0, r.x0); gx1 = max(gx1, r.x1)
                except Exception: pass
            clip = fitz.Rect(max(0, gx0 - 4), top + 2, min(W, gx1 + 4), min(H, y1 + 4))
            pix = p.get_pixmap(dpi=200, clip=clip)
            out = os.path.join(OUT, f'{key}_fig{n}.png'); pix.save(out); done.add(n)
            print(out, pi + 1, round(clip.width), round(clip.height))
