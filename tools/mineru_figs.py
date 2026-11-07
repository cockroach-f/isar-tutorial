"""Use local MinerU 4.1.7 (basic tier, ONNX layout) block bboxes to crop full figures via PyMuPDF at 300 dpi."""
import json,glob,hashlib,re,os,sys,fitz
from pathlib import Path
sys.path.insert(0,'tools')
PAPERS={'p1_DBSSIT':'01M68FJ1SEYH802Y8V3ZW4VWNC.pdf','p2_CVGNN':'01M68FJ1R3GHZ8V9GSG40HVVH8.pdf','p3_MSN':'01M68FJ1RD5ZHWJEQ2776FHSCW.pdf','p4_CvPGT':'01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf','p5_REMI':'01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p6_MLFR':'01M68FJ1QVRQND1JJGRHNQV3JD.pdf','p7_DCANet':'01M68FJ1RFCZKVMD8JS4M43190.pdf'}
OUT=Path('mineru_crops'); OUT.mkdir(exist_ok=True)
def txt(o):
    if isinstance(o,str): return o
    if isinstance(o,dict): return txt(o.get('content',''))
    if isinstance(o,list): return ' '.join(txt(x) for x in o)
    return ''
res={}
for key,pdf in PAPERS.items():
    path='/workspace/isar-papers/'+pdf; h=hashlib.sha256(open(path,'rb').read()).hexdigest()
    js=glob.glob(os.path.expanduser(f'~/.mineru/doclib/parsed/{h[:2]}/{h}/basic/*.json'))
    j=json.load(open(js[0])); doc=fitz.open(path)
    for pi,pg in enumerate(j['pages']):
        blocks=pg.get('blocks') or pg.get('content') or pg.get('para_blocks') or []
        if isinstance(pg,dict) and not blocks:
            blocks=[v for v in pg.values() if isinstance(v,list)][0]
        pending=[]
        for b in blocks:
            if b.get('type') not in ('image','chart','table'): continue
            pending.append(b['bbox'])
            caps=[c for c in b.get('content',[]) if isinstance(c,dict) and c.get('type','').endswith('_caption')]
            m=None
            for c in caps:
                m=m or re.match(r'\s*Fig(?:ure|\.)?\s*(\d+)',txt(c))
            if b['type']=='table' and not m: pending.pop(); continue
            if m:
                n=int(m.group(1)); pr=doc[pi].rect
                x0=min(p[0] for p in pending);y0=min(p[1] for p in pending);x1=max(p[2] for p in pending);y1=max(p[3] for p in pending)
                for c in caps: x0=min(x0,c['bbox'][0]);y0=min(y0,c['bbox'][1]);x1=max(x1,c['bbox'][2]);y1=max(y1,c['bbox'][3])
                r=fitz.Rect(x0*pr.width-4,y0*pr.height-4,x1*pr.width+4,y1*pr.height+4)&pr
                if (key,n) not in res:
                    doc[pi].get_pixmap(dpi=300,clip=r).save(OUT/f'{key}_fig{n}.png')
                    res[(key,n)]=(pi+1,[round(v) for v in r],len(pending))
                pending=[]
for k,v in sorted(res.items()): print(k,v)
print(len(res))
