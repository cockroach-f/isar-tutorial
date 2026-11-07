"""Manual re-crops (PDF pt coordinates, verified against page renders) for figures whose
automatic crop was truncated or mixed with neighbouring figures/tables. 300 dpi."""
import fitz, os
SRC = os.environ.get('ISAR_PAPERS_DIR', '/workspace/isar-papers')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'paper_figs')
FIX = {
 ('01M68FJ1R3GHZ8V9GSG40HVVH8.pdf','p2_CVGNN'): {4:(3,(306,259,542,370)), 5:(4,(310,52,565,198)), 6:(4,(310,200,558,338))},
 ('01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p5_REMI'): {8:(9,(47,186,565,465)), 10:(11,(47,49,565,202)), 11:(11,(47,203,565,483))},
 ('01M68FJ1RFCZKVMD8JS4M43190.pdf','p7_DCANet'): {6:(7,(47,53,565,296)), 10:(12,(47,240,565,659))},
 ('01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf','p4_CvPGT'): {12:(10,(316,392,558,510)), 13:(11,(306,172,550,434)), 14:(11,(306,440,550,614))},
}
for (fn, key), m in FIX.items():
    d = fitz.open(os.path.join(SRC, fn))
    for n, (pg, r) in m.items():
        d[pg-1].get_pixmap(dpi=300, clip=fitz.Rect(*r)).save(os.path.join(OUT, f'{key}_fig{n}.png'))
        print(key, n)
