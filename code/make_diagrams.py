# -*- coding: utf-8 -*-
"""自绘简化方法框图、分类体系图、阅读路线图 -> ../figures/  (python make_diagrams.py)"""
import os, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import isar_core as ic
ic.setup_cjk_font()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
COL = dict(in_='#dbeafe', pre='#fef3c7', net='#dcfce7', key='#fecaca', out='#e9d5ff', gray='#f1f5f9')

def diagram(name, nodes, edges, size=(14, 4.5), title=None, notes=None):
    fig, ax = plt.subplots(figsize=size); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis('off')
    pos = {}
    for k, (x, y, w, h, txt, c) in nodes.items():
        ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h, boxstyle='round,pad=0.4,rounding_size=1.5',
                                    fc=COL.get(c, c), ec='#334155', lw=1.2))
        ax.text(x, y, txt, ha='center', va='center', fontsize=9.5, wrap=True)
        pos[k] = (x, y, w, h)
    for e in edges:
        a, b = e[0], e[1]; lab = e[2] if len(e) > 2 else None; sty = e[3] if len(e) > 3 else '-'
        xa, ya, wa, ha = pos[a]; xb, yb, wb, hb = pos[b]
        if abs(ya - yb) > (ha + hb) / 2 + 1:          # 上下关系: 底边中点 -> 顶边中点
            sgn = 1 if yb < ya else -1
            p1 = (xa, ya - sgn * ha/2); p2 = (xb, yb + sgn * hb/2)
        else:                                          # 左右关系
            sgn = 1 if xb > xa else -1
            p1 = (xa + sgn * wa/2, ya); p2 = (xb - sgn * wb/2, yb)
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=14, color='#334155', lw=1.3, ls=sty,
                                     connectionstyle='arc3,rad=0'))
        if lab: ax.text((p1[0]+p2[0])/2, (p1[1]+p2[1])/2 + 2.5, lab, fontsize=8, ha='center', color='#b91c1c')
    ys = [v[1] - v[3]/2 for v in nodes.values()] + [v[1] + v[3]/2 for v in nodes.values()]
    lo, hi = min(ys) - (9 if notes else 4), max(ys) + 4
    ax.set_ylim(lo, hi); fig.set_size_inches(size[0], size[1] * (hi - lo) / 100 + 0.4)
    if title: ax.set_title(title, fontsize=13)
    if notes: ax.text(50, min(ys) - 6, notes, ha='center', fontsize=8.5, color='#475569')
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches='tight'); plt.close(fig); print('saved', name)

def p1():
    n = {'in': (7, 55, 11, 22, 'HH/HV/VV\n三通道\nISAR 像\n128×128', 'in_'),
         'pauli': (22, 55, 12, 22, 'Pauli 分解\n→ 相干矩阵 T\n→ 6维特征\nA~F', 'pre'),
         'mix': (37, 55, 12, 22, 'MixConv\n(3×3/5×5/7×7)\nBN+池化\n1×1卷积→3通道', 'pre'),
         'psfeb': (55, 78, 16, 18, 'PSFEB 极化散射分支\n分组卷积+交互卷积\n+极坐标注意力', 'key'),
         'sfeb': (55, 32, 16, 18, 'SFEB 空间分支\n卷积+深度卷积\n+空间注意力', 'net'),
         'stage': (55, 55, 12, 8, '×4 层级 stage', 'gray'),
         'lgfb': (74, 55, 12, 22, 'LGFB\n局部-全局融合\n(高效MHSA\n+多头卷积注意力)', 'key'),
         'out': (91, 55, 11, 18, 'BatchNorm\nSoftmax\n→ 6类', 'out')}
    e = [('in', 'pauli'), ('pauli', 'mix'), ('mix', 'psfeb'), ('mix', 'sfeb'), ('psfeb', 'lgfb'), ('sfeb', 'lgfb'), ('lgfb', 'out')]
    diagram('B1_dbssit_simple.png', n, e, title='论文1 DB-SSIT 简化框图 (自绘, 对应原文 Fig.1–5)',
            notes='思想: 一条支路看“极化散射机理”(通道间关系), 一条支路看“空间结构”(像素邻域), 最后用 Transformer 融合局部与全局')

def p2():
    n = {'in': (8, 55, 12, 22, '散焦的复值\nISAR 像\n(实部+虚部)', 'in_'),
         'cnn': (26, 55, 14, 22, '复值卷积\nCV-Conv + CV-BN\n→ 复特征向量', 'net'),
         'node': (45, 55, 14, 22, '节点 = 特征\n⊕ 标签\n已知:1+j0\n查询:1/N+j/N', 'pre'),
         'graph': (64, 55, 14, 22, '复值图网络\n邻接 |x_i−x_j|\n(实、虚分别)\nCV-Softmax', 'key'),
         'out': (84, 55, 14, 22, '查询节点输出\nN 维复概率\n→ 类别', 'out')}
    e = [('in', 'cnn'), ('cnn', 'node'), ('node', 'graph'), ('graph', 'out')]
    diagram('B2_cvgnn_simple.png', n, e, title='论文2 CV-GNN 简化框图 (自绘, 对应原文 Fig.2, Fig.6)',
            notes='思想: 不做重聚焦, 直接把“散焦复图像”的实部/虚部关系交给复值网络; 图网络在少样本间传递标签信息')

def p3():
    n = {'in': (7, 55, 11, 22, 'ISAR 像\n(仿真5类\n卫星)', 'in_'),
         'pre': (21, 55, 12, 22, '预处理\n增强Lee滤波\n幂变换\n能量归一化\n镜像扩增×4', 'pre'),
         'b1': (42, 82, 18, 14, '基学习器1: ResNet50+RAM\n(旋转注意力模块)', 'net'),
         'b2': (42, 55, 18, 14, '基学习器2: GCN\n(图卷积少样本)', 'net'),
         'b3': (42, 28, 18, 14, '基学习器3: 关系网络 RN', 'net'),
         'meta': (68, 55, 16, 26, '元学习器\n自适应加权\nXGBoost\n(Stacking,\n10折交叉生成\n元特征)', 'key'),
         'out': (90, 55, 11, 18, '5 类\n识别结果', 'out')}
    e = [('in', 'pre'), ('pre', 'b1'), ('pre', 'b2'), ('pre', 'b3'), ('b1', 'meta', '类别概率'), ('b2', 'meta'), ('b3', 'meta'), ('meta', 'out')]
    diagram('B3_msn_simple.png', n, e, title='论文3 MSN (元学习器 Stacking 网络) 简化框图 (自绘, 对应原文 Fig.5–10)',
            notes='思想: 三个“性格不同”的分类器各自给出概率, 再用 XGBoost 学习“该信谁”, 集成后更稳')

def p4():
    n = {'pre': (12, 82, 20, 14, '① 对比学习预训练\n随机成像参数生成 patch 对\nNT-Xent 损失', 'pre'),
         'enc': (12, 45, 18, 14, 'CV-ResNet18\n复值编码器\n(预训练后保留)', 'net'),
         'in': (12, 15, 16, 12, '复值 ISAR 像\n(支持/查询)', 'in_'),
         'patch': (36, 70, 16, 16, '分割→外接矩形\n→ N×N 重叠 patch\n→ 每 patch 编码', 'pre'),
         'gra': (55, 70, 15, 16, '② GRA 图推理\n8邻域强 patch 相连\n(局部结构)', 'key'),
         'tr': (74, 70, 15, 16, '复值 Transformer\n(全局关系)', 'key'),
         'glob': (55, 30, 15, 14, '整图嵌入网络\n(全局特征 E_w)', 'net'),
         'fuse': (74, 30, 15, 14, '特征融合\nE_f=[E_w,E_p]W', 'net'),
         'cls': (92, 50, 13, 22, '③ 图分类模块\n(GNN少样本)\n→ C-way\n类别', 'out')}
    e = [('pre', 'enc'), ('in', 'enc'), ('enc', 'patch'), ('patch', 'gra'), ('gra', 'tr'), ('enc', 'glob'), ('tr', 'fuse'), ('glob', 'fuse'), ('fuse', 'cls')]
    diagram('B4_cvpgt_simple.png', n, e, size=(14, 7), title='论文4 CvPGT 简化框图 (自绘, 对应原文 Fig.2–7)',
            notes='思想: 复值网络保留相位; 对比学习让特征对分辨率/散焦/旋转不敏感; patch 图 + Transformer 同时抓局部与全局')

def p5():
    n = {'in': (7, 55, 11, 20, 'ISAR 像\n(可能被拉伸/\n旋转/平移)', 'in_'),
         'stn': (24, 55, 15, 24, '多头 STN (MH-STN)\n3 个头各输出 5 参数\n平移2+缩放2+旋转1\n(无剪切, tanh 限幅)', 'key'),
         'cat': (40, 55, 11, 18, '3 张校正图\n+ 原图\n拼成 4 通道', 'pre'),
         'gen': (56, 55, 14, 24, 'GEN 组嵌入网络\n分组卷积 + 可变形\n卷积空间注意力\n+ 通道注意力\n→ (均值 z, 方差 s)', 'net'),
         'gat': (75, 55, 15, 24, 'MG-GAT\n高斯节点\n掩码注意力\n(只保留 top-k 邻居)', 'key'),
         'out': (92, 55, 10, 18, '查询类别\n(N-way)', 'out')}
    e = [('in', 'stn'), ('stn', 'cat'), ('cat', 'gen'), ('gen', 'gat'), ('gat', 'out')]
    diagram('B5_remi_simple.png', n, e, title='论文5 REMI 简化框图 (自绘, 对应原文 Fig.2–5)',
            notes='思想: 先“摆正”图像(鲁棒嵌入), 再在少样本图上用“带不确定度”的节点做稀疏推理(流形推理)')

def p6():
    n = {'in': (7, 55, 11, 22, 'S=3 个站\n同时刻的\nISAR 像', 'in_'),
         'g': (22, 55, 12, 18, '通道拼接\n分组卷积\n(每站一组)', 'net'),
         'isfr': (40, 55, 16, 26, 'ISFR 站间融合\n① AMFA: 各站仿射对齐\n(缩放/旋转/平移)\n② 轻量 Transformer\n跨站重建', 'key'),
         'conv': (57, 55, 10, 14, '后续\n卷积块', 'net'),
         'icfr': (72, 55, 14, 22, 'ICFR 类间融合\n(仅支持集)\n与“其它类均值”\n交互重建', 'key'),
         'inf': (90, 55, 13, 22, '原型+查询拼接\n关系模块打分\n→ 类别', 'out')}
    e = [('in', 'g'), ('g', 'isfr'), ('isfr', 'conv'), ('conv', 'icfr'), ('icfr', 'inf')]
    diagram('B6_mlfr_simple.png', n, e, title='论文6 MLFR 简化框图 (自绘, 对应原文 Fig.2–3)',
            notes='损失 = λ1 结构对齐(SSIM) + λ2 站重建(MSE) + λ3 类间对比(InfoNCE) + λ4 交叉熵; 思想: 先把多站“对齐成一个视角”, 再拉开类间差异')

def p7():
    n = {'in': (7, 55, 11, 22, '简缩极化\nS_LL, S_RL\n实+虚 → 4通道\n256×256', 'in_'),
         'det': (24, 55, 14, 22, '阶段1: RTMdet\nCSP 骨干 + PAFPN\n头1 → 旋转框\n(x,y,w,h,θ)+9类', 'net'),
         'mg': (42, 55, 14, 22, 'MGNF\n多高斯阈值→掩膜\n剔除目标外锚点\n(节点减少 71.74%)', 'pre'),
         'loc': (60, 78, 15, 16, '局部图: NMS 后\n最优框↔被抑制框\n(同类且 IoU≥0.1)', 'key'),
         'glo': (60, 32, 15, 16, '全局图: 最优框间\n类别分数余弦相似\nkNN (k=5)', 'key'),
         'fuse': (77, 55, 13, 18, 'GAT 聚合\n残差融合\n头2 精修', 'net'),
         'out': (93, 55, 10, 18, '部件旋转框\n+ 9 类部件', 'out')}
    e = [('in', 'det'), ('det', 'mg'), ('mg', 'loc'), ('mg', 'glo'), ('loc', 'fuse'), ('glo', 'fuse'), ('fuse', 'out')]
    diagram('B7_dcanet_simple.png', n, e, title='论文7 DCA-Net 简化框图 (自绘, 对应原文 Fig.4–6)',
            notes='思想: 识别从“整星是哪一类”细化到“星上每个部件在哪、是什么”; 用图注意力让冗余框/同类部件互相“商量”')

def taxonomy():
    n = {'root': (50, 90, 26, 9, 'ISAR 目标识别 (本文 7 篇)', 'gray'),
         'pol': (15, 65, 24, 10, '方向一: 极化 / 多特征', 'pre'),
         'fs': (50, 65, 24, 10, '方向二: 少样本 (Few-shot)', 'net'),
         'cv': (85, 65, 24, 10, '方向三: 复数域 (保留相位)', 'in_'),
         'a1': (8, 35, 14, 16, '论文1 DB-SSIT\n全极化 THz\n6类分类', 'pre'),
         'a7': (24, 35, 14, 16, '论文7 DCA-Net\n简缩极化\n部件级检测', 'pre'),
         'b3': (38, 35, 11, 16, '论文3 MSN\n集成学习\n小样本', 'net'),
         'b5': (52, 35, 11, 16, '论文5 REMI\n形变鲁棒\n元学习', 'net'),
         'b6': (66, 35, 11, 16, '论文6 MLFR\n多站融合\n元学习', 'net'),
         'c2': (80, 35, 11, 16, '论文2 CV-GNN\n散焦复图像\n+图网络', 'in_'),
         'c4': (93, 35, 11, 16, '论文4 CvPGT\n复值+对比\n+Patch图', 'in_')}
    e = [('root', 'pol'), ('root', 'fs'), ('root', 'cv'), ('pol', 'a1'), ('pol', 'a7'), ('fs', 'b3'), ('fs', 'b5'), ('fs', 'b6'), ('cv', 'c2'), ('cv', 'c4')]
    diagram('C1_taxonomy.png', n, e, size=(15, 7), title='七篇论文的分类体系 (自绘)',
            notes='注: 论文2、4 同时也是少样本方法; 论文5→6 为同一团队(西电)的延续; 论文3(2021)→2(2022)→4(2024) 为同一团队(哈工大)的延续')

def roadmap():
    n = {'s0': (8, 55, 12, 20, '第0步\nPart A 基础\n(RD成像/极化\n/深度学习)', 'gray'),
         's1': (25, 55, 12, 20, '第1步\n论文1 DB-SSIT\n(标准分类\n流程最清楚)', 'pre'),
         's2': (42, 55, 12, 20, '第2步\n论文7 DCA-Net\n(极化+检测)', 'pre'),
         's3': (60, 55, 14, 20, '第3步\n论文3 → 5 → 6\n(少样本主线)', 'net'),
         's4': (78, 55, 13, 20, '第4步\n论文2 → 4\n(复值网络)', 'in_'),
         's5': (93, 55, 10, 20, '第5步\n动手项目\n(Part C)', 'out')}
    e = [('s0', 's1'), ('s1', 's2'), ('s2', 's3'), ('s3', 's4'), ('s4', 's5')]
    diagram('C2_roadmap.png', n, e, size=(15, 3.8), title='推荐阅读路线 (自绘)')

if __name__ == '__main__':
    for f in [p1, p2, p3, p4, p5, p6, p7, taxonomy, roadmap]: f()
