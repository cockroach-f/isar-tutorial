"""对自动裁剪失败的若干原文插图做手工坐标裁剪 (PDF 坐标, 单位 pt)。"""
import fitz, os
SRC='/workspace/isar-papers'; OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','paper_figs')
FIX={('01M68FJ1SP4H4HRRH6H63YPJW5.pdf','p5_REMI'):{5:(6,(45,40,566,321)),6:(6,(45,321,566,499)),7:(6,(312,505,566,673))},
     ('01M68FJ1RFCZKVMD8JS4M43190.pdf','p7_DCANet'):{5:(4,(310,296,566,422))},
     ('01M68FJ1QF5PZDVW0M1F2KAKJ8.pdf','p4_CvPGT'):{11:(9,(45,300,306,492)),13:(10,(308,175,560,433))},
     ('01M68FJ1RD5ZHWJEQ2776FHSCW.pdf','p3_MSN'):{11:(10,(310,150,560,594))},
     ('01M68FJ1SEYH802Y8V3ZW4VWNC.pdf','p1_DBSSIT'):{1:(4,(52,80,305,698)),2:(4,(310,80,560,482)),3:(4,(310,486,560,727)),
        4:(6,(52,80,305,214)),5:(7,(52,80,305,324)),6:(7,(310,368,560,712)),7:(8,(52,80,305,220))}}
for (fn,key),m in FIX.items():
    d=fitz.open(os.path.join(SRC,fn))
    for n,(pg,r) in m.items():
        d[pg].get_pixmap(dpi=220,clip=fitz.Rect(*r)).save(os.path.join(OUT,f'{key}_fig{n}.png'))
print('done')
