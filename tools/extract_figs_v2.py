"""Re-extract paper figures from the original PDFs with PyMuPDF (no MinerU).
For each caption 'Fig. N' / 'Figure N': region = union of all images/vector drawings/short
text labels lying between the nearest body paragraph above (same column span) and the caption,
plus the caption itself. Rendered at 300 dpi. Also writes a page overlay for audit."""
import fitz, re, os, json, sys
SRC = os.environ.get('ISAR_PAPERS_DIR', '/workspace/isar-papers')
OUT = sys.argv[1]; AUD = sys.argv[2]
os.makedirs(OUT, exist_ok=True); os.makedirs(AUD, exist_ok=True)
PAPERS = {'p1_DBSSIT':'01M68FJ1SEYH802Y8V3ZW4VWNC.pdf','p2_CVGNN':'01M68FJ1R3GHZ8V9GSG40HVVH8.pdf',
          'p3_MSN':'01M68FJ1RD5ZHWJEQ2776FHSCW.pdf','p4_CvPGT':'01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf',
          'p5_REMI':'01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p6_MLFR':'01M68FJ1QVRQND1JJGRHNQV3JD.pdf',
          'p7_DCANet':'01M68FJ1RFCZKVMD8JS4M43190.pdf'}
cap_re = re.compile(r'^(Fig\.|Figure)\s*(\d+)[\.\s]')
meta = {}
for key, fn in PAPERS.items():
    d = fitz.open(os.path.join(SRC, fn)); done = set()
    for pi, p in enumerate(d):
        W, H = p.rect.width, p.rect.height
        blocks = [b for b in p.get_text('blocks') if b[6] == 0]
        gfx = [fitz.Rect(x['rect']) for x in p.get_drawings()]
        for im in p.get_images(full=True):
            try:
                for r in p.get_image_rects(im[0]): gfx.append(fitz.Rect(r))
            except Exception: pass
        gfx = [g for g in gfx if (g.width > 2 or g.height > 2) and g.width < 0.9*W and not (g.height > 0.5*H and g.width < 70)]
        for b in blocks:
            t = b[4].strip().replace('\n', ' ')
            m = cap_re.match(t)
            if not m or len(t) < 12: continue
            # skip in-text references like "Fig. 10 presents ..." (caption blocks start the line and are followed by description;
            # body references are inside long paragraphs that continue with lowercase verbs). Heuristic: caption blocks are
            # below graphics; require graphics directly above.
            n = int(m.group(2))
            if n in done: continue
            cap = fitz.Rect(b[:4])
            # candidate column span
            if cap.width > W*0.5: cx0, cx1 = 0, W
            elif cap.x1 <= W/2 + 15: cx0, cx1 = 0, W/2 + 5
            else: cx0, cx1 = W/2 - 5, W
            # graphics above caption overlapping column
            above = [g for g in gfx if g.y1 <= cap.y0 + 3 and cx0 <= (g.x0+g.x1)/2 <= cx1]
            # upper bound: nearest long body text block above caption in this column, with no graphics between
            top = 30
            for bb in blocks:
                bt = bb[4].strip()
                r = fitz.Rect(bb[:4])
                if r.y1 <= cap.y0 - 2 and r.x1 > cx0 + 5 and r.x0 < cx1 - 5 and (len(bt) > 200 or (cap_re.match(bt) and r != cap) or re.match(r'^(TABLE|Table)\s', bt) or len(re.findall(r'\d+\.\d\d', bt)) >= 3):
                    top = max(top, r.y1)
            region = [g for g in above if g.y0 >= top - 3]
            if not region: continue
            u = fitz.Rect(region[0])
            for g in region[1:]: u |= g
            if u.height < 25: continue
            # include short text labels (axis labels/legends/subpanel tags) inside or adjacent to the union
            for bb in blocks:
                r = fitz.Rect(bb[:4])
                if r.y0 >= top - 2 and r.y1 <= cap.y0 + 1 and len(bb[4].strip()) <= 200 and r.intersects(fitz.Rect(u.x0-25, u.y0-15, u.x1+25, u.y1+15)):
                    u |= r
            u |= cap
            clip = fitz.Rect(max(0, u.x0-4), max(0, u.y0-4), min(W, u.x1+4), min(H, u.y1+4))
            p.get_pixmap(dpi=300, clip=clip).save(os.path.join(OUT, f'{key}_fig{n}.png'))
            meta[f'{key}_fig{n}'] = {'page': pi+1, 'clip': [round(v,1) for v in clip]}
            done.add(n)
            # audit overlay
            pg = p.get_pixmap(dpi=60); import PIL.Image as I, PIL.ImageDraw as D
            im = I.frombytes('RGB', (pg.width, pg.height), pg.samples); dr = D.Draw(im); s = 60/72
            dr.rectangle([clip.x0*s, clip.y0*s, clip.x1*s, clip.y1*s], outline='red', width=3)
            im.save(os.path.join(AUD, f'{key}_fig{n}.png'))
json.dump(meta, open(os.path.join(OUT, '_clips.json'), 'w'), indent=1)
print(len(meta), 'figures')
