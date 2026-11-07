# -*- coding: utf-8 -*-
"""
isar_core.py —— 教学用 ISAR 仿真核心函数(纯 numpy, 无需深度学习框架)
=====================================================================
模型: 理想点散射体 + 转台模型 (translation 已补偿)
  雷达位于 +y 方向远场, 视线(LOS)沿 y 轴; 目标绕原点以角度 theta(t_m) 旋转。
  第 k 个散射点 (x_k, y_k) 在慢时间 t_m 的径向距离(远场近似):
      R_k(t_m) = y_k cos(theta) + x_k sin(theta)        (以转台中心为参考)
  频域(步进频/去斜后)回波:  s(f, t_m) = sum_k sigma_k exp(-j 4 pi f R_k(t_m) / c)
  距离压缩: 对 f 做 IFFT -> 一维距离像 (HRRP)
  方位压缩: 对 t_m 做 FFT -> 多普勒  => 距离-多普勒 (RD) ISAR 像
分辨率: 距离 rho_r = c / (2B);  横向(方位) rho_a = lambda / (2 * dtheta)
"""
import numpy as np

C = 3e8

def setup_cjk_font():
    """让 matplotlib 正确显示中文(Noto CJK)。"""
    import matplotlib
    from matplotlib import font_manager as fm
    for p in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
              '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
        try: fm.fontManager.addfont(p)
        except Exception: pass
    names = [f.name for f in fm.fontManager.ttflist if 'Noto Sans CJK' in f.name]
    pref = [n for n in names if n.endswith('SC')] or names
    if pref:
        matplotlib.rcParams['font.family'] = 'sans-serif'
        matplotlib.rcParams['font.sans-serif'] = [pref[0], 'DejaVu Sans']
    matplotlib.rcParams['axes.unicode_minus'] = False
    matplotlib.rcParams['mathtext.fontset'] = 'dejavusans'
    return pref[0] if pref else None

# ---------------------------------------------------------------- 目标模型
def satellite_points(kind='sat_a', seed=0):
    """返回 (N,2) 散射点坐标(m) 与 (N,) 复散射系数。几种简化“卫星”/目标形状。"""
    rng = np.random.default_rng(seed)
    pts, amp = [], []
    def add_rect(x0, x1, y0, y1, nx, ny, a=1.0):
        for x in np.linspace(x0, x1, nx):
            for y in np.linspace(y0, y1, ny):
                pts.append((x, y)); amp.append(a * (0.6 + 0.4 * rng.random()))
    if kind == 'sat_a':      # 立方体本体 + 左右两块太阳翼
        add_rect(-0.8, 0.8, -0.8, 0.8, 4, 4, 1.5)
        add_rect(-5.0, -1.2, -0.5, 0.5, 9, 3, 0.7)
        add_rect(1.2, 5.0, -0.5, 0.5, 9, 3, 0.7)
        pts += [(0, 1.6), (0, 2.2)]; amp += [2.0, 1.2]          # 天线杆
    elif kind == 'sat_b':    # 本体 + 单侧长太阳翼 + 抛物面天线
        add_rect(-1.0, 1.0, -0.6, 0.6, 4, 3, 1.5)
        add_rect(1.4, 6.0, -0.4, 0.4, 11, 2, 0.7)
        th = np.linspace(-0.9, 0.9, 9)
        for t in th: pts.append((-2.0 + 0.8*np.cos(t)*0, -0.0 + 1.6*np.sin(t))); amp.append(1.0)
        pts += [(-2.5, 0)]; amp += [2.5]
    elif kind == 'sat_c':    # 十字形: 本体 + 上下太阳翼 + 左右短杆
        add_rect(-0.7, 0.7, -0.7, 0.7, 3, 3, 1.5)
        add_rect(-0.4, 0.4, 1.1, 4.5, 2, 8, 0.7)
        add_rect(-0.4, 0.4, -4.5, -1.1, 2, 8, 0.7)
        pts += [(-2.0, 0), (-2.8, 0), (2.0, 0), (2.8, 0)]; amp += [1.2, 1.5, 1.2, 1.5]
    elif kind == 'sat_d':    # 长条形本体 + 两侧倾斜太阳翼
        add_rect(-0.5, 0.5, -2.5, 2.5, 2, 9, 1.3)
        for s in (-1, 1):
            for u in np.linspace(1.0, 4.0, 7):
                for v in np.linspace(-0.4, 0.4, 2):
                    x = s * u; y = v + 0.5 * s * u * 0.5
                    pts.append((x, y)); amp.append(0.7)
    elif kind == 'plane':    # 简化飞机: 机身 + 机翼 + 尾翼
        for y in np.linspace(-6, 6, 17): pts.append((0, y)); amp.append(1.0)
        for x in np.linspace(-6, 6, 15): pts.append((x, 0.5 - 0.15*abs(x))); amp.append(0.8)
        for x in np.linspace(-2.5, 2.5, 7): pts.append((x, -5.5)); amp.append(0.8)
        pts += [(0, 6.3), (-6, -0.4), (6, -0.4)]; amp += [2.0, 1.8, 1.8]
    else:
        raise ValueError(kind)
    pts = np.array(pts, float); amp = np.array(amp, float)
    phase = np.exp(1j * 2 * np.pi * rng.random(len(amp)))   # 随机初相(更接近真实)
    return pts, amp * phase

def rotate_pts(pts, ang):
    c, s = np.cos(ang), np.sin(ang)
    return pts @ np.array([[c, -s], [s, c]]).T

# ---------------------------------------------------------------- 回波与成像
def echo_turntable(pts, sig, fc=10e9, B=1e9, Nf=256, dtheta_deg=5.0, Np=256,
                   theta0_deg=0.0, alpha_ratio=0.0, snr_db=None, seed=0):
    """
    生成频域-慢时间回波矩阵 S[Np, Nf]。
    theta(t) 在 [-dtheta/2, dtheta/2] 内变化; alpha_ratio>0 时为非匀速转动:
        theta(u) = dtheta*u + alpha_ratio*dtheta*((u+1/2)^2 - 1/3),  u in [-1/2, 1/2) (归一化慢时间)
        即 θ = ωt + ½αt² 的形式; alpha_ratio = 二次项总转角 / 线性项总转角, 末端转速为初始的 (1+2·alpha_ratio) 倍
    """
    f = fc + np.linspace(-B/2, B/2, Nf, endpoint=False)
    u = np.linspace(-0.5, 0.5, Np, endpoint=False)
    th_lin = np.deg2rad(dtheta_deg) * u
    # 二次项用 (u+0.5)^2 (减去均值 1/3), 保证 alpha_ratio>=0 时转速单调增加(从 ω 加速到 (1+2·alpha_ratio)ω)
    th = np.deg2rad(theta0_deg) + th_lin + alpha_ratio * np.deg2rad(dtheta_deg) * ((u + 0.5)**2 - 1/3)
    x, y = pts[:, 0], pts[:, 1]
    R = y[None, :] * np.cos(th)[:, None] + x[None, :] * np.sin(th)[:, None]   # [Np, K]
    S = np.exp(-1j * 4 * np.pi * f[None, None, :] * R[:, :, None] / C)      # [Np,K,Nf]
    S = np.einsum('pkf,k->pf', S, sig)
    if snr_db is not None:
        rng = np.random.default_rng(seed)
        p = np.mean(np.abs(S)**2) / 10**(snr_db/10)
        S = S + np.sqrt(p/2) * (rng.standard_normal(S.shape) + 1j*rng.standard_normal(S.shape))
    return S, f, th

def range_profiles(S, win=True):
    """对频率维做 IFFT 得到一维距离像 HRRP (每个脉冲一条)。"""
    Nf = S.shape[1]
    w = np.hanning(Nf) if win else np.ones(Nf)
    return np.fft.fftshift(np.fft.ifft(S * w[None, :], axis=1), axes=1)

def rd_image(S, win=True):
    """距离-多普勒成像: 距离 IFFT + 方位 FFT。返回复图像 [Doppler, Range]。"""
    Np = S.shape[0]
    hrrp = range_profiles(S, win)
    w = np.hanning(Np) if win else np.ones(Np)
    # 注: 回波相位 exp(-j4πfR/c), x>0 的点 R 随 θ 增大 -> 负多普勒;
    #     这里对慢时间做 IFFT(等价于 FFT 后翻转), 使横向坐标与几何 x 同号, 便于对照。
    img = np.fft.fftshift(np.fft.ifft(hrrp * w[:, None], axis=0), axes=0)
    return img

def show_rd(ax, img, r_axis, a_axis, dyn=40, cmap='jet', title=None):
    """以 横轴=横向距离(多普勒), 纵轴=距离 显示 RD 像(dB)。"""
    im = ax.imshow(to_db(img, dyn).T, origin='lower', cmap=cmap, aspect='auto',
                   extent=[a_axis[0], a_axis[-1], r_axis[0], r_axis[-1]], vmin=-dyn, vmax=0)
    ax.set_xlabel('横向距离 / m'); ax.set_ylabel('距离 / m')
    if title: ax.set_title(title)
    return im

def axes_rd(fc, B, Nf, dtheta_deg, Np):
    """返回距离轴/横向距离轴 (m)。"""
    rr = C / (2 * B); lam = C / fc; ra = lam / (2 * np.deg2rad(dtheta_deg))
    r_axis = (np.arange(Nf) - Nf/2) * rr
    a_axis = (np.arange(Np) - Np/2) * ra
    return r_axis, a_axis, rr, ra

def to_db(img, dyn=40):
    a = np.abs(img); a = a / (a.max() + 1e-12)
    d = 20 * np.log10(a + 1e-12)
    return np.clip(d, -dyn, 0)

def image_entropy(img):
    p = np.abs(img)**2; p = p / p.sum()
    return float(-(p[p > 0] * np.log(p[p > 0])).sum())

# ---------------------------------------------------------------- LFM 与脉冲压缩
def lfm(T=10e-6, B=100e6, fs=400e6):
    t = np.arange(-T/2, T/2, 1/fs)
    k = B / T
    return t, np.exp(1j * np.pi * k * t**2), k

def matched_filter(x, ref):
    """匹配滤波 = 与参考信号共轭翻转做卷积 (频域实现)。"""
    n = len(x) + len(ref) - 1
    X = np.fft.fft(x, n)
    y = np.fft.ifft(X * np.conj(np.fft.fft(ref, n)))   # 频域: X(f) H*(f)
    return y[:len(x)]

# ---------------------------------------------------------------- 极化
def rot2(psi):
    c, s = np.cos(psi), np.sin(psi)
    return np.array([[c, -s], [s, c]])

def S_canonical(kind, psi=0.0):
    """典型散射体的 Sinclair 散射矩阵 [[HH, HV],[VH, VV]] (单位幅度, 简化)。"""
    if kind == 'trihedral' or kind == 'plate' or kind == 'sphere':   # 奇次(单次)散射
        S = np.eye(2)
    elif kind == 'dihedral':        # 偶次(二面角)散射
        S = np.diag([1.0, -1.0])
    elif kind == 'dipole':          # 细线/偶极子
        S = np.diag([1.0, 0.0])
    elif kind == 'helix_l':
        S = 0.5 * np.array([[1, 1j], [1j, -1]])
    else:
        raise ValueError(kind)
    R = rot2(psi)
    return R @ S @ R.T

def pauli_rgb(HH, HV, VV, dyn=30):
    """Pauli 伪彩色: R=|HH-VV|(偶次), G=2|HV|(体/旋转), B=|HH+VV|(奇次), 均按 1/sqrt2 归一。"""
    k1 = np.abs(HH + VV) / np.sqrt(2); k2 = np.abs(HH - VV) / np.sqrt(2); k3 = np.sqrt(2) * np.abs(HV)
    m = max(k1.max(), k2.max(), k3.max())
    def n(a):
        d = 20*np.log10(a/m + 1e-12); return np.clip((d + dyn) / dyn, 0, 1)
    return np.stack([n(k2), n(k3), n(k1)], -1)

def coherency_6d(HH, HV, VV, win=3):
    """按 DB-SSIT 论文式(2)-(9) 由 Pauli 矢量构造相干矩阵 T (局部 win×win 平均), 再转 6 维特征。
    注意: 论文式(7) 印刷为 D=|T12|/sqrt(T11*T33); 常见文献多为 sqrt(T11*T22)。此处两者都给出。"""
    from scipy.ndimage import uniform_filter
    k = np.stack([HH + VV, HH - VV, 2 * HV], 0) / np.sqrt(2)
    def avg(a): return uniform_filter(a.real, win) + 1j * uniform_filter(a.imag, win)
    T = {}
    for i in range(3):
        for j in range(3):
            T[(i, j)] = avg(k[i] * np.conj(k[j]))
    T11, T22, T33 = T[(0, 0)].real, T[(1, 1)].real, T[(2, 2)].real
    span = T11 + T22 + T33 + 1e-12
    eps = 1e-12
    A = 10 * np.log10(span)
    Bf = T22 / span; Cf = T33 / span
    D_printed = np.abs(T[(0, 1)]) / np.sqrt(T11 * T33 + eps)
    D_common = np.abs(T[(0, 1)]) / np.sqrt(T11 * T22 + eps)
    E = np.abs(T[(0, 2)]) / np.sqrt(T11 * T33 + eps)
    F = np.abs(T[(1, 2)]) / np.sqrt(T33 * T22 + eps)
    return dict(A=A, B=Bf, C=Cf, D_printed=D_printed, D_common=D_common, E=E, F=F)

def compact_pol_from_linear(HH, HV, VV, VH=None):
    """按 DCA-Net 论文式(2) (左旋圆极化发射, 左/右旋接收, DCP 模式):
       S_LL = (HH - VV)/2 + j(HV + VH)/2 ;  S_RL = (HH + VV)/2 + j(HV - VH)/2
    (圆极化基的符号约定随文献不同, 此处严格采用该论文给出的形式)"""
    if VH is None: VH = HV
    SLL = (HH - VV) / 2 + 1j * (HV + VH) / 2
    SRL = (HH + VV) / 2 + 1j * (HV - VH) / 2
    return SLL, SRL

# ---------------------------------------------------------------- 散射中心提取 & 图
def extract_scatter_centers(img_abs, thr_db=-18, nmax=40, nms=3):
    """非常简化的散射中心提取: 局部极大值 + 阈值 (可视作 CLEAN 的粗糙替代)。"""
    from scipy.ndimage import maximum_filter
    a = img_abs / img_abs.max()
    loc = (a == maximum_filter(a, size=2*nms+1)) & (20*np.log10(a+1e-12) > thr_db)
    ys, xs = np.nonzero(loc)
    v = a[ys, xs]; o = np.argsort(-v)[:nmax]
    return np.stack([xs[o], ys[o]], 1), v[o]

def knn_edges(P, k=3):
    E = set()
    D = np.linalg.norm(P[:, None] - P[None], axis=-1)
    for i in range(len(P)):
        for j in np.argsort(D[i])[1:k+1]:
            E.add(tuple(sorted((i, int(j)))))
    return sorted(E)

def make_dataset(kinds, n_per=20, fc=10e9, B=1e9, Nf=128, dtheta=5.0, Np=128,
                 az_range=(0, 360), seed=0, snr_db=20):
    """生成小型 RD-ISAR 数据集 (幅度, 归一化 dB->[0,1]) 用于入门实验。返回 X[N,H,W], y[N]。"""
    rng = np.random.default_rng(seed)
    X, y = [], []
    for ci, k in enumerate(kinds):
        pts, sig = satellite_points(k, seed=ci)
        for n in range(n_per):
            az = rng.uniform(*az_range)
            p = rotate_pts(pts, np.deg2rad(az))
            S, _, _ = echo_turntable(p, sig, fc, B, Nf, dtheta, Np, snr_db=snr_db, seed=int(rng.integers(1e9)))
            im = (to_db(rd_image(S), 40) + 40) / 40
            X.append(im.astype(np.float32)); y.append(ci)
    return np.stack(X), np.array(y)

# ---------------------------------------------------------------- 参数化随机“卫星”类别 (少样本实验用)
def random_target(cid):
    """由类别编号 cid 确定性地生成一个“卫星”类别: 本体尺寸、太阳翼长度/数目/倾角、天线位置等。
    同一 cid 总是同一几何(同一类), 不同 cid 几何不同。可生成任意多类, 便于划分基类/新类。"""
    rng = np.random.default_rng(1000 + cid)
    pts, amp = [], []
    bw, bh = rng.uniform(0.6, 1.5), rng.uniform(0.6, 1.8)
    for x in np.linspace(-bw, bw, 4):
        for y in np.linspace(-bh, bh, 4):
            pts.append((x, y)); amp.append(1.5)
    nw = rng.integers(1, 3)                       # 1 或 2 块太阳翼
    L = rng.uniform(2.5, 5.5); tilt = rng.uniform(-0.4, 0.4); wid = rng.uniform(0.3, 0.8)
    sides = [1] if nw == 1 else [-1, 1]
    for s in sides:
        for u in np.linspace(bw + 0.4, bw + 0.4 + L, int(L / 0.45)):
            for v in np.linspace(-wid, wid, 2):
                pts.append((s * u, v + tilt * u)); amp.append(0.7)
    na = rng.integers(0, 3)                        # 天线/杆
    for i in range(na):
        ang = rng.uniform(0, 2*np.pi); d = rng.uniform(1.5, 3.0)
        pts.append((d*np.cos(ang), d*np.sin(ang))); amp.append(rng.uniform(1.5, 2.5))
    pts = np.array(pts); amp = np.array(amp) * (0.6 + 0.4*rng.random(len(amp)))
    return pts, amp * np.exp(1j*2*np.pi*rng.random(len(amp)))

def simulate_image(pts, sig, az_deg, fc=10e9, B=1e9, N=64, dtheta=5.0, snr_db=20, seed=0, crop=None):
    """单张幅度 RD 像, 归一化到 [0,1] (40 dB 动态范围)。"""
    p = rotate_pts(pts, np.deg2rad(az_deg))
    S, _, _ = echo_turntable(p, sig, fc, B, N, dtheta, N, snr_db=snr_db, seed=seed)
    im = ((to_db(rd_image(S), 40) + 40) / 40).T.astype(np.float32)
    return im
