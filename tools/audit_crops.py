"""Locate each existing crop on its PDF page (template matching) and test whether any
image/vector graphic is cut by the crop border (=> truncated) ."""
import fitz, cv2, numpy as np, json, os, sys, re
SRC='/workspace/isar-papers'; FIG=sys.argv[1]
P={'p1_DBSSIT':'01M68FJ1SEYH802Y8V3ZW4VWNC.pdf','p2_CVGNN':'01M68FJ1R3GHZ8V9GSG40HVVH8.pdf','p3_MSN':'01M68FJ1RD5ZHWJEQ2776FHSCW.pdf','p4_CvPGT':'01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf','p5_REMI':'01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p6_MLFR':'01M68FJ1QVRQND1JJGRHNQV3JD.pdf','p7_DCANet':'01M68FJ1RFCZKVMD8JS4M43190.pdf'}
used=[l.strip() for l in open(sys.argv[2])]
S=50/72; res={}
for k in used:
    key=k.rsplit('_fig',1)[0]; d=fitz.open(os.path.join(SRC,P[key]))
    crop=cv2.imread(f'{FIG}/{k}.png',0); best=None
    for dpi in (200,220,300):
        t=cv2.resize(crop,None,fx=50/dpi,fy=50/dpi,interpolation=cv2.INTER_AREA)
        for pi,p in enumerate(d):
            pix=p.get_pixmap(dpi=50,colorspace=fitz.csGRAY); im=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width)
            if t.shape[0]>im.shape[0] or t.shape[1]>im.shape[1]: continue
            r=cv2.matchTemplate(im,t,cv2.TM_CCOEFF_NORMED); _,mv,_,ml=cv2.minMaxLoc(r)
            if best is None or mv>best[0]: best=(mv,pi,ml,t.shape,dpi)
    mv,pi,(x,y),(h,w),dpi=best; p=d[pi]
    R=fitz.Rect(x/S,y/S,(x+w)/S,(y+h)/S)
    g=[fitz.Rect(z['rect']) for z in p.get_drawings()]
    for im in p.get_images(full=True):
        try: g+= [fitz.Rect(r) for r in p.get_image_rects(im[0])]
        except: pass
    cut=[]
    for r in g:
        if r.width<3 and r.height<3: continue
        if r.width>0.9*p.rect.width or (r.height>0.5*p.rect.height and r.width<70): continue
        inter=r & R
        if inter.is_empty or inter.get_area()<=0: continue
        out=r.get_area()-inter.get_area()
        if out>0.08*r.get_area() and out>40: cut.append([round(v) for v in r])
    res[k]={'score':round(mv,3),'page':pi+1,'rect':[round(v,1) for v in R],'cut':cut[:6],'ncut':len(cut)}
    print(k,res[k]['score'],'p',pi+1,'ncut',len(cut),cut[:3])
json.dump(res,open('/tmp/audit.json','w'),indent=1)
