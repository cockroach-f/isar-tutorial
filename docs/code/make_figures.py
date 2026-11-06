# -*- coding: utf-8 -*-
"""生成教学文档 Part A 的全部仿真配图 -> ../figures/   运行: python make_figures.py"""
import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, Polygon
import isar_core as ic

ic.setup_cjk_font()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures'); os.makedirs(OUT, exist_ok=True)
def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches='tight'); plt.close(fig); print('saved', name)

# ---------------------------------------------------------------- 1. LFM
def fig_lfm():
    T, B, fs = 10e-6, 100e6, 400e6
    t, s, k = ic.lfm(T, B, fs)
    fig, ax = plt.subplots(1, 3, figsize=(13, 3.4))
    ax[0].plot(t*1e6, s.real, lw=0.7); ax[0].set_title('LFM 信号实部 (T=10 μs, B=100 MHz)')
    ax[0].set_xlabel('时间 / μs'); ax[0].set_ylabel('幅度')
    ax[1].plot(t*1e6, k*t/1e6, 'r'); ax[1].set_title('瞬时频率 f(t)=K·t 线性变化')
    ax[1].set_xlabel('时间 / μs'); ax[1].set_ylabel('频率 / MHz')
    n = 8192; Sf = np.fft.fftshift(np.fft.fft(s, n)); fr = np.fft.fftshift(np.fft.fftfreq(n, 1/fs))
    ax[2].plot(fr/1e6, 20*np.log10(np.abs(Sf)/np.abs(Sf).max()+1e-9)); ax[2].set_ylim(-40, 3)
    ax[2].set_title('频谱: 近似矩形, 宽度≈B'); ax[2].set_xlabel('频率 / MHz'); ax[2].set_ylabel('dB')
    for a in ax: a.grid(alpha=.3)
    save(fig, 'A01_lfm.png')

# ---------------------------------------------------------------- 2. 脉冲压缩
def fig_pulse_compression():
    fs = 800e6; T = 10e-6
    fig, ax = plt.subplots(2, 2, figsize=(12, 6.2))
    d = 2.5   # 两目标相距 2.5 m
    for col, B in enumerate([20e6, 200e6]):
        t, ref, k = ic.lfm(T, B, fs)
        N = len(t) + 2000
        tau1 = 400; tau2 = tau1 + int(round(2*d/ic.C*fs))
        x = np.zeros(N, complex); x[tau1:tau1+len(ref)] += ref; x[tau2:tau2+len(ref)] += 0.7*ref
        y = ic.matched_filter(x, ref)
        tt = np.arange(N)/fs*1e6
        ax[0, col].plot(tt, x.real, lw=.5); ax[0, col].set_title(f'回波(两目标相距 {d} m, B={B/1e6:.0f} MHz): 互相重叠')
        rr = np.arange(N)/fs*ic.C/2
        yy = np.abs(y)/np.abs(y).max()
        ax[1, col].plot(rr - rr[tau1], yy); ax[1, col].set_xlim(-5, 10)
        ax[1, col].set_title(f'匹配滤波后: 距离分辨率 c/2B = {ic.C/2/B:.2f} m')
        ax[1, col].set_xlabel('相对距离 / m'); ax[0, col].set_xlabel('时间 / μs')
        for a in ax[:, col]: a.grid(alpha=.3)
    fig.tight_layout(); save(fig, 'A02_pulse_compression.png')

# ---------------------------------------------------------------- 3. 转台几何
def fig_turntable():
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    a = ax[0]; a.set_aspect('equal'); a.axis('off')
    a.add_patch(Polygon([[-0.4, 7.6], [0.4, 7.6], [0, 7.0]], color='k'))
    a.text(0.6, 7.3, '雷达 (远场)', fontsize=12)
    a.annotate('', xy=(0, 1.2), xytext=(0, 6.8), arrowprops=dict(arrowstyle='->', lw=1.5, color='gray'))
    a.text(0.15, 4.5, '雷达视线 LOS\n(距离向 y)', color='gray')
    pts, _ = ic.satellite_points('sat_a'); p = ic.rotate_pts(pts, np.deg2rad(20)) * 0.35
    a.scatter(p[:, 0], p[:, 1], s=10, c='C0')
    a.add_patch(Circle((0, 0), 2.1, fill=False, ls='--', color='C1'))
    a.annotate('', xy=(1.6, 1.5), xytext=(2.1, 0.3), arrowprops=dict(arrowstyle='->', color='C1', lw=2, connectionstyle='arc3,rad=0.3'))
    a.text(2.2, 1.2, 'ω 转动', color='C1', fontsize=12)
    a.plot([0, 2.6], [0, 0], 'k:', lw=1); a.text(2.7, -0.1, 'x (横向)')
    q = p[5]; a.plot(*q, 'ro'); a.annotate('散射点 (x_k, y_k)', xy=q, xytext=(-3.3, -1.9), color='r', arrowprops=dict(arrowstyle='->', color='r'))
    a.set_xlim(-3.5, 4); a.set_ylim(-2.6, 8)
    a.set_title('ISAR 转台模型: 平动补偿后, 目标相当于绕中心旋转')
    # 右: 多普勒与 x 的关系
    b = ax[1]
    om = np.deg2rad(5)/1.0; lam = 0.03
    xs = np.array([-4, -2, 0, 2, 4])
    for x in xs:
        b.plot([x, x], [0, 2*om*x/lam], lw=3)
    b.axhline(0, color='k', lw=.8)
    b.set_xlabel('散射点横向坐标 x / m'); b.set_ylabel('多普勒频率 f_d / Hz')
    b.set_title('f_d = 2ωx/λ : 多普勒 ∝ 横向位置\n(λ=3 cm, ω=5°/s)')
    b.grid(alpha=.3)
    save(fig, 'A03_turntable.png')

# ---------------------------------------------------------------- 4. 目标->HRRP->RD
P0 = dict(fc=10e9, B=1e9, Nf=256, dtheta_deg=5.0, Np=256)
def fig_hrrp_rd():
    pts, sig = ic.satellite_points('sat_a')
    pts = ic.rotate_pts(pts, np.deg2rad(25))
    S, f, th = ic.echo_turntable(pts, sig, **P0)
    hr = ic.range_profiles(S); img = ic.rd_image(S)
    r, a, rr, ra = ic.axes_rd(P0['fc'], P0['B'], P0['Nf'], P0['dtheta_deg'], P0['Np'])
    fig, ax = plt.subplots(1, 4, figsize=(17, 4.2))
    ax[0].scatter(pts[:, 0], pts[:, 1], s=np.abs(sig)*15); ax[0].set_aspect('equal')
    ax[0].set_title('(a) 点散射体目标模型'); ax[0].set_xlabel('x / m'); ax[0].set_ylabel('y (视线) / m'); ax[0].grid(alpha=.3)
    ax[1].imshow(np.abs(S.real), aspect='auto', cmap='gray', origin='lower',
                 extent=[(f[0]-P0['fc'])/1e6, (f[-1]-P0['fc'])/1e6, 0, P0['Np']])
    ax[1].set_title('(b) 原始回波 Re{s(f,t_m)}'); ax[1].set_xlabel('频率偏移 / MHz'); ax[1].set_ylabel('脉冲序号 (慢时间)')
    ax[2].imshow(ic.to_db(hr, 40), aspect='auto', cmap='jet', origin='lower', extent=[r[0], r[-1], 0, P0['Np']])
    ax[2].set_title('(c) 距离压缩: HRRP 历程'); ax[2].set_xlabel('距离 / m'); ax[2].set_ylabel('脉冲序号')
    ic.show_rd(ax[3], img, r, a, title='(d) 方位 FFT 后: RD 像 (dB)')
    ax[3].set_xlim(-9, 9); ax[3].set_ylim(-9, 9)
    fig.tight_layout(); save(fig, 'A04_target_hrrp_rd.png')
    # 单条 HRRP
    fig, axx = plt.subplots(figsize=(8, 3))
    axx.plot(r, np.abs(hr[P0['Np']//2])/np.abs(hr).max()); axx.set_xlim(-8, 8)
    axx.set_xlabel('距离 / m'); axx.set_ylabel('归一化幅度'); axx.set_title('一维距离像 HRRP: 目标在雷达视线上的“投影”'); axx.grid(alpha=.3)
    save(fig, 'A05_hrrp_single.png')

def fig_resolution_grid():
    pts, sig = ic.satellite_points('sat_a'); pts = ic.rotate_pts(pts, np.deg2rad(25))
    fig, ax = plt.subplots(2, 2, figsize=(10, 9))
    for i, B in enumerate([0.3e9, 1.5e9]):
        for j, dth in enumerate([1.5, 6.0]):
            S, _, _ = ic.echo_turntable(pts, sig, 10e9, B, 256, dth, 256)
            r, a, rr, ra = ic.axes_rd(10e9, B, 256, dth, 256)
            ic.show_rd(ax[i, j], ic.rd_image(S), r, a, title=f'B={B/1e9:.1f} GHz, Δθ={dth}°\nρr={rr*100:.0f} cm, ρa={ra*100:.0f} cm')
            ax[i, j].set_xlim(-8, 8); ax[i, j].set_ylim(-8, 8)
    fig.suptitle('分辨率: 带宽 B 决定距离向, 转角 Δθ 决定横向 (fc=10 GHz)', fontsize=13)
    fig.tight_layout(); save(fig, 'A06_resolution_grid.png')

def fig_defocus():
    pts, sig = ic.satellite_points('sat_a'); pts = ic.rotate_pts(pts, np.deg2rad(25))
    fig, ax = plt.subplots(1, 4, figsize=(17, 4.3))
    r, a, rr, ra = ic.axes_rd(**{k: P0[k] for k in ['fc', 'B', 'Nf', 'dtheta_deg', 'Np']})
    for j, al in enumerate([0, 0.3, 1.0]):
        S, _, _ = ic.echo_turntable(pts, sig, **P0, alpha_ratio=al)
        img = ic.rd_image(S)
        ic.show_rd(ax[j], img, r, a, title=f'角加速度项比例={al}  熵={ic.image_entropy(img):.2f}')
        ax[j].set_xlim(-8, 8); ax[j].set_ylim(-8, 8)
    # MTRC: 大转角 + 大目标
    big = pts * 3.0
    S, _, _ = ic.echo_turntable(big, sig, 10e9, 1e9, 256, 20.0, 1024)
    r2, a2, _, _ = ic.axes_rd(10e9, 1e9, 256, 20.0, 1024)
    ic.show_rd(ax[3], ic.rd_image(S), r2, a2, title='大转角(20°)+大目标: MTRC 散焦')
    ax[3].set_xlim(-18, 18); ax[3].set_ylim(-18, 18)
    fig.tight_layout(); save(fig, 'A07_defocus.png')

# ---------------------------------------------------------------- 极化
def fig_pol_canonical():
    kinds = [('trihedral', 0, '三面角/平板 (奇次)'), ('dihedral', 0, '二面角 0° (偶次)'),
             ('dihedral', np.pi/4, '二面角 45° (偶次, 旋转)'), ('dipole', 0, '水平偶极子'), ('dipole', np.pi/4, '45° 偶极子')]
    fig, ax = plt.subplots(1, len(kinds), figsize=(16, 3.4), sharey=True)
    for a, (k, psi, name) in zip(ax, kinds):
        S = ic.S_canonical(k, psi)
        vals = [abs(S[0, 0]), abs(S[0, 1]), abs(S[1, 1])]
        a.bar(['|HH|', '|HV|', '|VV|'], vals, color=['C0', 'C2', 'C3'])
        a.set_title(name, fontsize=10); a.set_ylim(0, 1.1)
        a.text(0.5, -0.33, 'S=' + np.array2string(np.round(S.real, 2), separator=',').replace('\n', ''),
               transform=a.transAxes, ha='center', fontsize=8)
    fig.suptitle('典型散射体的极化“指纹”', y=1.03); save(fig, 'A08_pol_canonical.png')

def pol_target():
    """构造一个各部件散射机理不同的目标: 本体=二面角, 太阳翼=平板, 天线杆=偶极子(45°)。"""
    pts, sig = ic.satellite_points('sat_a')
    n = len(pts); typ = []
    for (x, y) in pts:
        if abs(x) <= 0.9 and abs(y) <= 0.9: typ.append(('dihedral', 0.0))
        elif abs(x) < 0.1 and y > 1.0: typ.append(('dipole', np.pi/4))
        else: typ.append(('trihedral', 0.0))
    pts = ic.rotate_pts(pts, np.deg2rad(25))
    ch = {}
    for name, (i, j) in {'HH': (0, 0), 'HV': (0, 1), 'VV': (1, 1)}.items():
        s = np.array([sig[k] * ic.S_canonical(*typ[k])[i, j] for k in range(n)])
        S, _, _ = ic.echo_turntable(pts, s, **P0)
        ch[name] = ic.rd_image(S)
    return ch

def fig_pol_target():
    ch = pol_target()
    r, a, _, _ = ic.axes_rd(**{k: P0[k] for k in ['fc', 'B', 'Nf', 'dtheta_deg', 'Np']})
    m = max(np.abs(v).max() for v in ch.values())
    fig, ax = plt.subplots(2, 3, figsize=(14, 9))
    ext = [a[0], a[-1], r[0], r[-1]]
    for j, k in enumerate(['HH', 'HV', 'VV']):
        d = np.clip(20*np.log10(np.abs(ch[k])/m + 1e-12), -40, 0)
        ax[0, j].imshow(d.T, origin='lower', cmap='jet', extent=ext, vmin=-40, vmax=0, aspect='auto')
        ax[0, j].set_title(f'{k} 通道 (共同归一化, dB)')
    rgb = ic.pauli_rgb(ch['HH'], ch['HV'], ch['VV'])
    ax[1, 0].imshow(np.transpose(rgb, (1, 0, 2)), origin='lower', extent=ext, aspect='auto')
    ax[1, 0].set_title('Pauli 伪彩色: R=|HH-VV| G=|2HV| B=|HH+VV|')
    SLL, SRL = ic.compact_pol_from_linear(ch['HH'], ch['HV'], ch['VV'])
    mm = max(np.abs(SLL).max(), np.abs(SRL).max())
    def nd(x): return np.clip((20*np.log10(np.abs(x)/mm + 1e-12) + 30)/30, 0, 1)
    pc = np.stack([nd(SLL), nd(SLL - SRL), nd(SRL)], -1)
    ax[1, 1].imshow(np.transpose(pc, (1, 0, 2)), origin='lower', extent=ext, aspect='auto')
    ax[1, 1].set_title('简缩极化伪彩色 (按 DCA-Net 式2/3):\nR=|S_LL| G=|S_LL-S_RL| B=|S_RL|')
    f6 = ic.coherency_6d(ch['HH'], ch['HV'], ch['VV'])
    ax[1, 2].imshow(np.clip(f6['A'] - f6['A'].max(), -40, 0).T, origin='lower', cmap='jet', extent=ext, aspect='auto')
    ax[1, 2].set_title('DB-SSIT 6维特征之 A: 总功率 Span (dB)')
    for x in ax.ravel(): x.set_xlim(-7, 7); x.set_ylim(-7, 7); x.set_xlabel('横向/m'); x.set_ylabel('距离/m')
    fig.text(0.5, -0.01, '目标设定: 本体=二面角(偶次,红), 太阳翼=平板(奇次,蓝), 天线杆=45°偶极子(产生交叉极化,绿)', ha='center')
    fig.tight_layout(); save(fig, 'A09_pol_target.png')
    # 6 维特征全图
    fig, ax = plt.subplots(1, 6, figsize=(18, 3.3))
    names = [('A', 'A: Span(dB)'), ('B', 'B: T22/Span'), ('C', 'C: T33/Span'), ('D_printed', 'D: |T12|/√(T11T33)\n(按论文式7印刷)'),
             ('E', 'E: |T13|/√(T11T33)'), ('F', 'F: |T23|/√(T33T22)')]
    mask = f6['A'] > f6['A'].max() - 35
    for x, (k, t) in zip(ax, names):
        v = f6[k].copy(); v = np.where(mask, v, np.nan)
        x.imshow(v.T, origin='lower', cmap='viridis', extent=ext, aspect='auto'); x.set_title(t, fontsize=9)
        x.set_xlim(-7, 7); x.set_ylim(-7, 7); x.set_xticks([]); x.set_yticks([])
    fig.suptitle('由 HH/HV/VV 计算的 6 维极化特征 (仅显示 Span>-35 dB 的像素)', y=1.05)
    save(fig, 'A10_pol_6d.png')

# ---------------------------------------------------------------- 为什么难
def fig_why_hard():
    fig, ax = plt.subplots(2, 4, figsize=(15, 7.6))
    r, a, _, _ = ic.axes_rd(10e9, 1e9, 256, 5.0, 256)
    for j, az in enumerate([0, 30, 60, 90]):
        pts, sig = ic.satellite_points('sat_a'); p = ic.rotate_pts(pts, np.deg2rad(az))
        S, _, _ = ic.echo_turntable(p, sig, 10e9, 1e9, 256, 5.0, 256, snr_db=15, seed=j)
        ic.show_rd(ax[0, j], ic.rd_image(S), r, a, title=f'同一目标 A, 方位 {az}°')
    for j, (k, az) in enumerate([('sat_a', 10), ('sat_c', 80), ('sat_d', 5), ('sat_b', 0)]):
        pts, sig = ic.satellite_points(k); p = ic.rotate_pts(pts, np.deg2rad(az))
        S, _, _ = ic.echo_turntable(p, sig, 10e9, 1e9, 256, 5.0, 256, snr_db=15, seed=j)
        ic.show_rd(ax[1, j], ic.rd_image(S), r, a, title=f'目标 {k[-1].upper()}, 方位 {az}°')
    for x in ax.ravel(): x.set_xlim(-8, 8); x.set_ylim(-8, 8)
    fig.suptitle('ISAR 识别之难: 上排 同类不同姿态差异大 (类内差异); 下排 不同类可能相似 (类间相似)', fontsize=13)
    fig.tight_layout(); save(fig, 'A11_why_hard.png')

# ---------------------------------------------------------------- 复数图像
def fig_complex():
    pts, sig = ic.satellite_points('sat_a'); p = ic.rotate_pts(pts, np.deg2rad(25))
    S, _, _ = ic.echo_turntable(p, sig, **P0)
    img = ic.rd_image(S)
    r, a, _, _ = ic.axes_rd(**{k: P0[k] for k in ['fc', 'B', 'Nf', 'dtheta_deg', 'Np']})
    ext = [a[0], a[-1], r[0], r[-1]]
    fig, ax = plt.subplots(1, 4, figsize=(17, 4))
    m = np.abs(img).max()
    ax[0].imshow(ic.to_db(img).T, origin='lower', cmap='jet', extent=ext, aspect='auto'); ax[0].set_title('幅度 |I| (dB)')
    ph = np.angle(img); ph = np.where(np.abs(img) > m*0.03, ph, np.nan)
    ax[1].imshow(ph.T, origin='lower', cmap='hsv', extent=ext, aspect='auto'); ax[1].set_title('相位 ∠I (仅强像素)')
    ax[2].imshow((img.real/m).T, origin='lower', cmap='RdBu', extent=ext, aspect='auto', vmin=-.3, vmax=.3); ax[2].set_title('实部 Re{I}')
    ax[3].imshow((img.imag/m).T, origin='lower', cmap='RdBu', extent=ext, aspect='auto', vmin=-.3, vmax=.3); ax[3].set_title('虚部 Im{I}')
    for x in ax: x.set_xlim(-7, 7); x.set_ylim(-7, 7)
    fig.suptitle('ISAR 像本质上是复数: 实值网络只用幅度, 复值网络(论文2、4)同时利用相位', y=1.03)
    save(fig, 'A12_complex_image.png')

# ---------------------------------------------------------------- 散射点图
def fig_scatter_graph():
    pts, sig = ic.satellite_points('sat_a'); p = ic.rotate_pts(pts, np.deg2rad(25))
    S, _, _ = ic.echo_turntable(p, sig, **P0)
    img = ic.rd_image(S); A = np.abs(img).T
    r, a, rr, ra = ic.axes_rd(**{k: P0[k] for k in ['fc', 'B', 'Nf', 'dtheta_deg', 'Np']})
    P, v = ic.extract_scatter_centers(A, thr_db=-22, nmax=40, nms=3)
    xy = np.stack([a[P[:, 0]], r[P[:, 1]]], 1)
    E = ic.knn_edges(xy, 3)
    ext = [a[0], a[-1], r[0], r[-1]]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.8))
    ax[0].imshow(ic.to_db(img).T, origin='lower', cmap='jet', extent=ext, aspect='auto'); ax[0].set_title('(a) ISAR 像')
    ax[1].imshow(ic.to_db(img).T, origin='lower', cmap='gray', extent=ext, aspect='auto')
    ax[1].scatter(xy[:, 0], xy[:, 1], s=40*v+5, c='r'); ax[1].set_title(f'(b) 提取强散射点 (局部极大+阈值, {len(xy)} 个)')
    for i, j in E: ax[2].plot(*xy[[i, j]].T, 'gray', lw=1)
    ax[2].scatter(xy[:, 0], xy[:, 1], s=60*v+10, c=v, cmap='autumn_r', zorder=3, edgecolors='k')
    ax[2].set_title('(c) 构图: 节点=散射点, 边=k 近邻 (k=3)'); ax[2].set_facecolor('#f4f4f4')
    for x in ax: x.set_xlim(-7, 7); x.set_ylim(-7, 7); x.set_xlabel('横向/m'); x.set_ylabel('距离/m')
    fig.tight_layout(); save(fig, 'A13_scatter_graph.png')

# ---------------------------------------------------------------- few-shot episode
def fig_episode():
    kinds = ['sat_a', 'sat_b', 'sat_c', 'sat_d', 'plane']
    rng = np.random.default_rng(3)
    fig = plt.figure(figsize=(14, 6.2))
    gs = fig.add_gridspec(3, 6, width_ratios=[1, 1, 1, 1, 1, 0.1])
    r, a, _, _ = ic.axes_rd(10e9, 1e9, 128, 5.0, 128)
    for c, k in enumerate(kinds):
        pts, sig = ic.satellite_points(k, seed=c)
        for row in range(3):
            az = rng.uniform(0, 360)
            S, _, _ = ic.echo_turntable(ic.rotate_pts(pts, np.deg2rad(az)), sig, 10e9, 1e9, 128, 5.0, 128, snr_db=20, seed=row)
            ax = fig.add_subplot(gs[row, c]); ax.imshow(ic.to_db(ic.rd_image(S)).T, origin='lower', cmap='jet', aspect='auto')
            ax.set_xticks([]); ax.set_yticks([]); ax.set_xlim(20, 108); ax.set_ylim(20, 108)
            col = 'tab:blue' if row == 0 else 'tab:orange'
            for s in ax.spines.values(): s.set_edgecolor(col); s.set_linewidth(3)
            if row == 0: ax.set_title(f'类别 {c+1}\n支持样本 (K=1)', color=col, fontsize=10)
            else: ax.set_title(f'查询样本 #{row}', color=col, fontsize=9)
    fig.suptitle('一个 5-way 1-shot 任务(episode): 每类只给 1 张带标签的支持图(蓝), 对查询图(橙)分类\n'
                 '训练时从“基类”反复采样这样的小任务; 测试时用从未见过的“新类”组成任务', fontsize=12, y=1.04)
    save(fig, 'A14_fewshot_episode.png')

def fig_prototype():
    rng = np.random.default_rng(1)
    cs = np.array([[0, 0], [4, 1], [1.5, 4], [5, 5], [-2, 4]])
    fig, ax = plt.subplots(1, 2, figsize=(13, 5.3))
    for K, x in zip([1, 5], ax):
        for i, c in enumerate(cs):
            s = c + rng.normal(0, 0.9, (K, 2)); pro = s.mean(0)
            x.scatter(*s.T, c=f'C{i}', s=40, alpha=.6)
            x.scatter(*pro, c=f'C{i}', marker='*', s=400, edgecolors='k', zorder=4)
        q = np.array([2.6, 2.3]); x.scatter(*q, c='k', marker='X', s=180, zorder=5)
        x.text(q[0]+.2, q[1]-.5, '查询 q')
        x.set_title(f'{K}-shot: ★=原型(支持样本嵌入的均值)\n分类: q 归到距离最近的原型'); x.grid(alpha=.3)
        x.set_xlabel('嵌入维度 1'); x.set_ylabel('嵌入维度 2')
    fig.suptitle('原型网络 (Prototypical Network) 的直观示意 (嵌入空间, 示意数据)', y=1.04)
    save(fig, 'A15_prototype.png')

# ---------------------------------------------------------------- STN
def fig_stn():
    from scipy.ndimage import affine_transform
    pts, sig = ic.satellite_points('sat_c'); S, _, _ = ic.echo_turntable(pts, sig, 10e9, 1e9, 128, 5.0, 128)
    im = (ic.to_db(ic.rd_image(S)).T + 40)/40
    def aff(M, t=(0, 0)):
        c = np.array(im.shape)/2; Mi = np.linalg.inv(M)
        return affine_transform(im, Mi, offset=c - Mi@(c + np.array(t)), order=1)
    th = np.deg2rad(25)
    cases = [('原图', np.eye(2), (0, 0)), ('旋转 25°', np.array([[np.cos(th), -np.sin(th)], [np.sin(th), np.cos(th)]]), (0, 0)),
             ('横向缩放 0.7 (转速不同)', np.diag([1, 0.7]), (0, 0)), ('平移 (残余平动)', np.eye(2), (8, -10)),
             ('剪切 (CvPGT 约束中去掉)', np.array([[1, 0.4], [0, 1]]), (0, 0))]
    fig, ax = plt.subplots(1, 5, figsize=(17, 3.6))
    for x, (t, M, tr) in zip(ax, cases):
        x.imshow(aff(M, tr), origin='lower', cmap='jet'); x.set_title(t, fontsize=10); x.set_xticks([]); x.set_yticks([])
        x.set_xlim(15, 113); x.set_ylim(15, 113)
    fig.suptitle('空间变换网络(STN)学习的仿射变换: ISAR 像的旋转/尺度/平移变化可由仿射矩阵描述', y=1.05)
    save(fig, 'A16_stn_affine.png')

# ---------------------------------------------------------------- 卷积 & 注意力 示意
def fig_conv():
    from scipy.signal import convolve2d
    pts, sig = ic.satellite_points('sat_a'); S, _, _ = ic.echo_turntable(pts, sig, 10e9, 1e9, 128, 5.0, 128)
    im = (ic.to_db(ic.rd_image(S)).T + 40)/40
    ks = {'水平边缘核': np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]]), '竖直边缘核': np.array([[-1, 0, 1]]*3),
          '平滑核': np.ones((3, 3))/9}
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8))
    ax[0].imshow(im, origin='lower', cmap='gray'); ax[0].set_title('输入 ISAR 像')
    for x, (n, k) in zip(ax[1:], ks.items()):
        x.imshow(convolve2d(im, k, mode='same'), origin='lower', cmap='RdBu'); x.set_title(f'{n}\n{np.round(k,2).tolist()}', fontsize=8)
    for x in ax: x.set_xticks([]); x.set_yticks([]); x.set_xlim(20, 108); x.set_ylim(20, 108)
    fig.suptitle('卷积 = 用小模板在图上滑动做加权求和; CNN 自动学习这些模板', y=1.04)
    save(fig, 'A17_conv.png')

def fig_attention():
    pts, sig = ic.satellite_points('sat_a'); S, _, _ = ic.echo_turntable(ic.rotate_pts(pts, 0.4), sig, 10e9, 1e9, 128, 5.0, 128)
    im = (ic.to_db(ic.rd_image(S)).T + 40)/40; im = im[16:112, 16:112]
    P = 12; n = im.shape[0]//P
    tok = im.reshape(n, P, n, P).transpose(0, 2, 1, 3).reshape(n*n, -1)
    tok = tok - tok.mean(1, keepdims=True)
    q = tok[(n//2)*n + n//2]
    att = np.exp(tok@q / np.sqrt(tok.shape[1]) * 0.6); att = att/att.sum()
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.4))
    ax[0].imshow(im, origin='lower', cmap='gray')
    for i in range(1, n): ax[0].axhline(i*P-.5, color='y', lw=.6); ax[0].axvline(i*P-.5, color='y', lw=.6)
    ax[0].add_patch(Rectangle((n//2*P-.5, n//2*P-.5), P, P, fill=False, ec='r', lw=2))
    ax[0].set_title(f'切成 {n}×{n} 个 patch (token); 红框为查询 token')
    ax[1].imshow(att.reshape(n, n), origin='lower', cmap='hot'); ax[1].set_title('查询 token 对所有 token 的注意力权重\nsoftmax(q·k/√d)')
    ax[2].axis('off')
    ax[2].text(0, .5, '自注意力:\n  Q = XW_Q,  K = XW_K,  V = XW_V\n  Attn(Q,K,V) = softmax(QK^T/√d)·V\n\n'
               '每个 token 根据与其它 token 的相似度\n“加权汇总”全局信息 → 捕捉远距离\n散射结构关系(如两块太阳翼之间)',
               fontsize=12, va='center')
    for x in ax[:2]: x.set_xticks([]); x.set_yticks([])
    fig.suptitle('Transformer 注意力机制示意 (权重为简化计算, 仅作直观说明)', y=1.02)
    save(fig, 'A18_attention.png')

def fig_contrastive():
    rng = np.random.default_rng(5)
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for k, x in enumerate(ax):
        for i in range(4):
            c = np.array([np.cos(i*np.pi/2), np.sin(i*np.pi/2)]) * (2.5 if k else 0.8)
            s = c + rng.normal(0, 0.9 if k == 0 else 0.35, (12, 2))
            x.scatter(*s.T, c=f'C{i}', s=30)
        x.set_aspect('equal'); x.grid(alpha=.3); x.set_xlim(-4.5, 4.5); x.set_ylim(-4.5, 4.5)
    ax[0].set_title('对比学习之前: 各类嵌入混杂'); ax[1].set_title('对比学习之后: 同一目标的“增强视图”靠近,\n不同目标推远 (NT-Xent 损失)')
    fig.suptitle('对比学习示意 (示意数据)'); save(fig, 'A19_contrastive.png')

def fig_mag_vs_phase_swap():
    """经典实验: 交换两幅图的幅度/相位, 说明相位携带结构信息。"""
    r, a, _, _ = ic.axes_rd(10e9, 1e9, 128, 5.0, 128)
    I = []
    for k in ['sat_a', 'sat_c']:
        pts, sig = ic.satellite_points(k); S, _, _ = ic.echo_turntable(pts, sig, 10e9, 1e9, 128, 5.0, 128)
        I.append(S)   # 在“频率-慢时间”域交换(=图像的二维傅里叶域)
    sw1 = np.abs(I[0])*np.exp(1j*np.angle(I[1])); sw2 = np.abs(I[1])*np.exp(1j*np.angle(I[0]))
    fig, ax = plt.subplots(1, 4, figsize=(15, 3.8))
    for x, s, t in zip(ax, [I[0], I[1], sw1, sw2], ['目标A 像', '目标C 像', 'A的幅度+C的相位(回波域)', 'C的幅度+A的相位(回波域)']):
        x.imshow(ic.to_db(ic.rd_image(s)).T, origin='lower', cmap='jet'); x.set_title(t, fontsize=10); x.set_xticks([]); x.set_yticks([])
        x.set_xlim(20, 108); x.set_ylim(20, 108)
    fig.suptitle('回波域交换幅度/相位: 成像结果“像谁”主要由相位决定 —— 相位携带目标结构信息', y=1.04)
    save(fig, 'A20_phase_swap.png')

if __name__ == '__main__':
    for fn in [fig_lfm, fig_pulse_compression, fig_turntable, fig_hrrp_rd, fig_resolution_grid, fig_defocus,
               fig_pol_canonical, fig_pol_target, fig_why_hard, fig_complex, fig_scatter_graph, fig_episode,
               fig_prototype, fig_stn, fig_conv, fig_attention, fig_contrastive, fig_mag_vs_phase_swap]:
        fn()
