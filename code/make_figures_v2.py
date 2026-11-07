# -*- coding: utf-8 -*-
"""v2 新增的基础概念配图 (例题配套) -> ../figures/v2_*.png"""
import os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle, FancyBboxPatch
import isar_core as ic
ic.setup_cjk_font()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'figures')
def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches='tight'); plt.close(fig); print('saved', name)
def arrow(ax, p, q, c='k', lw=1.6, txt=None, **kw):
    ax.annotate('', xy=q, xytext=p, arrowprops=dict(arrowstyle='-|>', color=c, lw=lw, **kw))
    if txt: ax.text(*q, txt, color=c, fontsize=11)

def f01_complex():
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
    a = ax[0]; a.set_aspect('equal'); a.grid(alpha=.3); a.axhline(0, c='k', lw=.8); a.axvline(0, c='k', lw=.8)
    arrow(a, (0, 0), (3, 4), 'C0', txt='  z = 3+4j'); a.plot([3, 3], [0, 4], 'C0:'); a.plot([0, 3], [4, 4], 'C0:')
    arrow(a, (0, 0), (-4, 3), 'C3', txt=' z·$e^{j90^\\circ}$ = −4+3j')
    t = np.linspace(0, np.arctan2(4, 3), 50); a.plot(1.2*np.cos(t), 1.2*np.sin(t), 'C0'); a.text(1.3, .5, 'φ=53.13°', color='C0')
    a.text(1.0, 2.4, '|z|=5', color='C0'); a.set_xlim(-5, 5); a.set_ylim(-1, 5.5)
    a.set_xlabel('实部 (I)'); a.set_ylabel('虚部 (Q)'); a.set_title('(a) 复数 = 平面上的箭头 (相量)')
    b = ax[1]; tt = np.linspace(0, 2, 400)
    for ph, c in [(0, 'C0'), (np.pi/3, 'C3')]:
        b.plot(tt, np.cos(2*np.pi*1*tt + ph), c, label=f'cos(2πt + {np.degrees(ph):.0f}°)')
    b.legend(loc='upper right'); b.grid(alpha=.3); b.set_xlabel('时间 t / s'); b.set_title('(b) 相位 = 波形的“起跑位置”')
    c = ax[2]; th = np.linspace(0, 2*np.pi, 13)[:-1]
    for i, x in enumerate(th):
        c.annotate('', xy=(np.cos(x), np.sin(x)), xytext=(0, 0), arrowprops=dict(arrowstyle='-|>', color=plt.cm.viridis(i/12)))
    c.set_aspect('equal'); c.set_xlim(-1.3, 1.3); c.set_ylim(-1.3, 1.3); c.grid(alpha=.3)
    c.set_title('(c) $e^{j\\omega t}$: 箭头匀速旋转\n每个时刻的投影 = cos 与 sin'); c.set_xlabel('I'); c.set_ylabel('Q')
    save(fig, 'v2_01_complex.png')

def f02_iq():
    fs = 20000; t = np.arange(0, 0.05, 1/fs); fc = 200; A, ph = 2, np.pi/3
    x = A*np.cos(2*np.pi*fc*t + ph)
    i_raw = x*2*np.cos(2*np.pi*fc*t); q_raw = -x*2*np.sin(2*np.pi*fc*t)
    win = int(fs/fc)  # 滑动平均窗口 = 一个载波周期, 恰好消掉 2fc 分量 (最简单的低通)
    I = np.convolve(i_raw, np.ones(win)/win, 'same'); Q = np.convolve(q_raw, np.ones(win)/win, 'same')
    I[:win] = I[-win:] = np.nan; Q[:win] = Q[-win:] = np.nan
    fig, ax = plt.subplots(1, 3, figsize=(15, 3.8))
    ax[0].plot(t*1e3, x); ax[0].set_title('(a) 接收到的实信号 x(t)=2cos(2π·200t+60°)'); ax[0].set_xlabel('t / ms')
    ax[1].plot(t*1e3, i_raw, alpha=.4, label='乘 2cos 后'); ax[1].plot(t*1e3, I, 'C3', lw=2, label='低通后 I≈1.0')
    ax[1].plot(t*1e3, Q, 'C2', lw=2, label='低通后 Q≈1.732'); ax[1].legend(fontsize=8); ax[1].set_title('(b) 混频 + 低通 = 取出 I、Q'); ax[1].set_xlabel('t / ms')
    ax[2].set_aspect('equal'); ax[2].grid(alpha=.3); arrow(ax[2], (0, 0), (1, 1.732), 'C3', txt=' I+jQ = 2$e^{j60^\\circ}$')
    ax[2].set_xlim(-.5, 2.5); ax[2].set_ylim(-.5, 2.3); ax[2].set_title('(c) I、Q 合成复数: 幅度 2, 相位 60°'); ax[2].set_xlabel('I'); ax[2].set_ylabel('Q')
    for a in ax[:2]: a.grid(alpha=.3)
    save(fig, 'v2_02_iq.png')

def f03_fourier():
    fs = 1000; t = np.arange(0, 1, 1/fs); x = np.cos(2*np.pi*50*t) + 0.5*np.cos(2*np.pi*120*t)
    X = np.fft.fftshift(np.fft.fft(x))/len(x); f = np.fft.fftshift(np.fft.fftfreq(len(x), 1/fs))
    fig, ax = plt.subplots(1, 3, figsize=(15, 3.8))
    ax[0].plot(t[:200]*1e3, x[:200]); ax[0].set_title('(a) 时域: cos(2π·50t)+0.5cos(2π·120t)'); ax[0].set_xlabel('t / ms')
    ax[1].plot(f, np.abs(X), 'C0'); ax[1].set_xlim(-200, 200); ax[1].set_title('(b) 频谱 |X(f)|: ±50 Hz 高 0.5, ±120 Hz 高 0.25'); ax[1].set_xlabel('f / Hz')
    n = np.arange(4); xs = np.array([1, 0, -1, 0]); Xk = np.fft.fft(xs)
    ax[2].stem(n - 0.08, xs, linefmt='C0-', markerfmt='C0o', basefmt=' ', label='x[n]=[1,0,−1,0]')
    ax[2].stem(n + 0.08, np.abs(Xk), linefmt='C3-', markerfmt='C3s', basefmt=' ', label='|X[k]|=[0,2,0,2]')
    ax[2].legend(); ax[2].set_xticks(n); ax[2].set_title('(c) 4 点 DFT 手算例题'); ax[2].set_xlabel('n 或 k')
    for a in ax: a.grid(alpha=.3)
    save(fig, 'v2_03_fourier.png')

def f04_sampling():
    t = np.linspace(0, 0.2, 2000); fs = 40; ts = np.arange(0, 0.2, 1/fs)
    fig, ax = plt.subplots(1, 2, figsize=(13, 3.8))
    ax[0].plot(t, np.cos(2*np.pi*30*t), 'C0', alpha=.6, label='真实 30 Hz')
    ax[0].plot(t, np.cos(2*np.pi*10*t), 'C3--', label='看起来像 10 Hz')
    ax[0].plot(ts, np.cos(2*np.pi*30*ts), 'ko', label='fs = 40 Hz 的采样点'); ax[0].legend(fontsize=8, loc='lower right')
    ax[0].set_title('(a) 欠采样 (fs < 2f): 30 Hz 被“混叠”成 10 Hz'); ax[0].set_xlabel('t / s')
    ts2 = np.arange(0, 0.2, 1/100)
    ax[1].plot(t, np.cos(2*np.pi*30*t), 'C0', alpha=.6); ax[1].plot(ts2, np.cos(2*np.pi*30*ts2), 'ko')
    ax[1].set_title('(b) fs = 100 Hz > 2×30 Hz: 采样点能唯一确定波形'); ax[1].set_xlabel('t / s')
    for a in ax: a.grid(alpha=.3)
    save(fig, 'v2_04_sampling.png')

def f05_barker():
    s = np.array([1, 1, -1.]); r = np.zeros(8); r[1:4] += s; r[4:7] += 0.5*s
    y = np.correlate(r, s, 'valid')
    fig, ax = plt.subplots(1, 3, figsize=(15, 3.6))
    ax[0].stem(range(3), s, basefmt=' '); ax[0].set_title('(a) 发射码 s = [1, 1, −1]'); ax[0].set_xticks(range(3))
    ax[1].stem(range(8), r, basefmt=' '); ax[1].set_title('(b) 接收: 目标A 延迟1 (幅度1) + 目标B 延迟4 (幅度0.5)'); ax[1].set_xticks(range(8))
    ax[2].stem(range(len(y)), y, basefmt=' '); ax[2].set_title('(c) 匹配滤波输出 y = [0, 3, −0.5, −1, 1.5, 0]\n峰在 1 和 4: 正是两个延迟'); ax[2].set_xticks(range(len(y)))
    for a in ax: a.grid(alpha=.3); a.set_xlabel('样本序号 n')
    save(fig, 'v2_05_barker.png')

def f06_doppler_phase():
    lam = 0.03; om = 0.05; PRF = 20; tm = np.arange(0, 2, 1/PRF)
    fig, ax = plt.subplots(1, 2, figsize=(13, 4))
    for x, c in [(2.0, 'C0'), (-1.0, 'C3')]:
        ph = -4*np.pi/lam * x*om*tm
        ax[0].plot(tm, np.unwrap(ph), c, label=f'x = {x} m'); 
        sig = np.exp(1j*ph); F = np.fft.fftshift(np.fft.fft(sig, 512)); f = np.fft.fftshift(np.fft.fftfreq(512, 1/PRF))
        ax[1].plot(f, np.abs(F)/len(tm), c, label=f'x = {x} m → $f_d$ = {-2*om*x/lam:.2f} Hz')
    ax[0].set_title('(a) 同一距离单元内, 散射点相位随慢时间线性变化'); ax[0].set_xlabel('慢时间 $t_m$ / s'); ax[0].set_ylabel('相位 / rad'); ax[0].legend()
    ax[1].set_title('(b) 对慢时间做 FFT: 斜率(=多普勒)变成频谱峰位置'); ax[1].set_xlabel('多普勒 / Hz'); ax[1].legend(); ax[1].set_xlim(-10, 10)
    for a in ax: a.grid(alpha=.3)
    save(fig, 'v2_06_doppler_phase.png')

def f07_defocus_if():
    T = 2; t = np.linspace(-T/2, T/2, 400); lam = 0.03; x = 3; om = 0.05
    fig, ax = plt.subplots(1, 2, figsize=(13, 4))
    for al, c in [(0, 'C0'), (0.01, 'C3')]:
        ax[0].plot(t, -2*x*(om + al*t)/lam, c, label=f'α = {al} rad/s²')
        ph = -4*np.pi/lam*x*(om*t + 0.5*al*t**2); F = np.fft.fftshift(np.fft.fft(np.exp(1j*ph)*np.hanning(len(t)), 4096))
        f = np.fft.fftshift(np.fft.fftfreq(4096, t[1]-t[0])); ax[1].plot(f, np.abs(F)/np.abs(F).max(), c, label=f'α = {al}')
    ax[0].set_title('(a) 瞬时多普勒 $f_d(t)$ = −2x(ω+αt)/λ\n(x=3 m, ω=0.05 rad/s, λ=3 cm)'); ax[0].set_xlabel('t / s'); ax[0].set_ylabel('Hz'); ax[0].legend()
    ax[1].set_xlim(-16, -4); ax[1].set_title('(b) 方位谱: 匀速 → 一根尖峰; 加速 → 展宽约 4 Hz (≈8 个分辨单元)'); ax[1].set_xlabel('多普勒 / Hz'); ax[1].legend()
    for a in ax: a.grid(alpha=.3)
    save(fig, 'v2_07_defocus_if.png')

def f08_neuron():
    fig, ax = plt.subplots(1, 2, figsize=(14, 4.2))
    a = ax[0]; a.axis('off'); a.set_xlim(0, 10); a.set_ylim(0, 6)
    for (y, lab) in [(4.5, 'x$_1$ = 1'), (1.5, 'x$_2$ = 2')]:
        a.add_patch(Circle((1, y), .45, fc='#dbeafe', ec='k')); a.text(1, y, lab.split()[0], ha='center', va='center'); a.text(0.0, y+.6, lab)
    a.add_patch(Circle((5, 3), .8, fc='#fde68a', ec='k')); a.text(5, 3, 'Σ + b\n→ σ', ha='center', va='center')
    arrow(a, (1.45, 4.4), (4.25, 3.3)); arrow(a, (1.45, 1.6), (4.25, 2.7))
    a.text(2.6, 4.2, 'w$_1$ = 0.5'); a.text(2.6, 1.55, 'w$_2$ = 0.2'); a.text(4.6, 4.1, 'b = 0.1')
    arrow(a, (5.8, 3), (8.2, 3)); a.text(6.0, 3.3, 'z = 1.0'); a.text(8.3, 2.9, 'ReLU: 1.0\nsigmoid: 0.731')
    a.set_title('(a) 一个神经元的例题: z = 0.5×1 + 0.2×2 + 0.1 = 1.0')
    z = np.linspace(-4, 4, 200); b = ax[1]
    b.plot(z, np.maximum(z, 0), label='ReLU = max(0,z)'); b.plot(z, 1/(1+np.exp(-z)), label='sigmoid'); b.plot(z, np.tanh(z), label='tanh')
    b.plot(z, np.where(z > 0, z, 0.1*z), '--', label='LeakyReLU (0.1)'); b.legend(); b.grid(alpha=.3); b.set_ylim(-1.5, 4)
    b.set_title('(b) 常见激活函数'); b.set_xlabel('z')
    save(fig, 'v2_08_neuron.png')

def f09_gd():
    w = np.linspace(-0.2, 1.4, 200); L = (2*w - 1)**2
    ws = [0.8]; lr = 0.1
    for _ in range(4): ws.append(ws[-1] - lr*2*(2*ws[-1]-1)*2)
    fig, ax = plt.subplots(figsize=(7, 4)); ax.plot(w, L, 'k'); 
    for i, ww in enumerate(ws):
        ax.plot(ww, (2*ww-1)**2, 'o', c=plt.cm.autumn(i/5), ms=9, label=f'第 {i} 步: w = {ww:.4f}, L = {(2*ww-1)**2:.4f}')
    ax.legend(loc='upper left')
    ax.set_xlabel('w'); ax.set_ylabel('L(w) = (2w − 1)²'); ax.grid(alpha=.3)
    ax.set_title('梯度下降例题: x=2, y=1, 学习率 0.1, 从 w=0.8 出发')
    save(fig, 'v2_09_gd.png')

def f10_conv():
    X = np.array([[1, 2, 0, 1], [0, 1, 3, 1], [2, 1, 0, 0], [1, 0, 1, 2]]); K = np.array([[1, 0, -1]]*3)
    Y = np.array([[(X[i:i+3, j:j+3]*K).sum() for j in range(2)] for i in range(2)])
    fig, ax = plt.subplots(1, 3, figsize=(13, 4.2))
    def grid(a, M, title, hl=None, cmap='Blues'):
        a.imshow(M, cmap=cmap, alpha=.35); a.set_xticks([]); a.set_yticks([]); a.set_title(title)
        for i in range(M.shape[0]):
            for j in range(M.shape[1]): a.text(j, i, f'{M[i,j]:g}', ha='center', va='center', fontsize=15)
        if hl: a.add_patch(Rectangle((hl[1]-.5, hl[0]-.5), hl[2], hl[2], fill=False, ec='r', lw=3))
    grid(ax[0], X, '(a) 输入 4×4 (红框为第一个窗口)', (0, 0, 3)); grid(ax[1], K, '(b) 3×3 卷积核 (竖直边缘检测)', cmap='Oranges')
    grid(ax[2], Y, '(c) 输出 2×2\n左上 = (1+0+2) − (0+3+0) = 0', (0, 0, 1), cmap='Greens')
    save(fig, 'v2_10_conv.png')

def f11_attention():
    X = np.array([[1, 0], [0, 1], [1, 1.]]); S = X@X.T/np.sqrt(2); A = np.exp(S); A /= A.sum(1, keepdims=True)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
    for a, M, t in [(ax[0], S, r'(a) 打分 $QK^T/\sqrt{d}$'), (ax[1], A, '(b) 按行 softmax 后的注意力权重')]:
        a.imshow(M, cmap='Reds'); a.set_xticks(range(3)); a.set_yticks(range(3))
        a.set_xticklabels(['k$_1$', 'k$_2$', 'k$_3$']); a.set_yticklabels(['q$_1$', 'q$_2$', 'q$_3$']); a.set_title(t)
        for i in range(3):
            for j in range(3): a.text(j, i, f'{M[i,j]:.3f}', ha='center', va='center', fontsize=13)
    fig.suptitle('3 个 token 的自注意力例题: x$_1$=[1,0], x$_2$=[0,1], x$_3$=[1,1], 取 $W_Q=W_K=W_V=I$', y=1.02)
    save(fig, 'v2_11_attention.png')

def f12_gnn():
    P = np.array([[0, 0], [2, 0], [4, 0]]); h0 = ['[1, 0]', '[0, 1]', '[1, 1]']; h1 = ['[0.5, 0.5]', '[0.667, 0.667]', '[0.5, 1]']
    fig, ax = plt.subplots(1, 2, figsize=(13, 3))
    for a, hh, t in [(ax[0], h0, '(a) 第 0 层: 初始特征 (边 1–2, 2–3)'), (ax[1], h1, '(b) 一次消息传递后 (自己+邻居 取平均)')]:
        a.plot(P[:, 0], P[:, 1], 'k-', lw=2, zorder=1)
        for i, (p, s) in enumerate(zip(P, hh)):
            a.add_patch(Circle(p, .45, fc=['#dbeafe', '#fde68a', '#dcfce7'][i], ec='k', zorder=2)); a.text(*p, f'{i+1}', ha='center', va='center', fontsize=14, zorder=3)
            a.text(p[0], -0.95, s, ha='center', fontsize=12)
        a.set_xlim(-1, 5); a.set_ylim(-1.4, 0.8); a.set_aspect('equal'); a.axis('off'); a.set_title(t)
    save(fig, 'v2_12_gnn.png')

def f13_proto():
    c = np.array([[1, 0], [0, 1], [-1, -1]]); q = np.array([0.6, 0.3]); d = ((c-q)**2).sum(1); p = np.exp(-d)/np.exp(-d).sum()
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    for i in range(3):
        ax.scatter(*c[i], s=500, marker='*', c=f'C{i}', edgecolors='k', zorder=3); ax.text(c[i][0]+.08, c[i][1]+.12, f'原型 c{i+1}', fontsize=11)
        ax.plot(*np.stack([q, c[i]]).T, '--', c=f'C{i}'); m = (q + c[i])/2
        off = [(0.15, -0.55), (-0.75, 0.1), (-0.2, 0.0)][i]
        ax.text(m[0]+off[0], m[1]+off[1], f'd²={d[i]:.2f}\np={p[i]:.3f}', fontsize=10, bbox=dict(fc='w', alpha=.85))
    ax.scatter(*q, marker='X', s=200, c='k', zorder=4); ax.text(q[0]-.1, q[1]+.25, '查询 q = [0.6, 0.3]')
    ax.grid(alpha=.3); ax.set_aspect('equal'); ax.set_xlim(-1.5, 1.6); ax.set_ylim(-1.5, 1.5)
    ax.set_title('3-way 1-shot 原型网络例题: q 被判为类别 1 (p=0.638)')
    save(fig, 'v2_13_proto.png')

def f14_complexmul():
    w = 1+2j; x = 3-1j; y = w*x
    fig, ax = plt.subplots(figsize=(6, 5))
    for z, c, t in [(x, 'C0', 'x = 3 − j'), (w, 'C2', 'w = 1 + 2j'), (y, 'C3', 'w·x = 5 + 5j')]:
        arrow(ax, (0, 0), (z.real, z.imag), c, txt='  ' + t)
    ax.set_aspect('equal'); ax.grid(alpha=.3); ax.axhline(0, c='k', lw=.7); ax.axvline(0, c='k', lw=.7)
    ax.set_xlim(-1, 7); ax.set_ylim(-2, 6); ax.set_title('复数乘法 = 幅度相乘、相位相加\n|w|=2.236, |x|=3.162 → |wx|=7.071; 63.4° + (−18.4°) = 45°')
    save(fig, 'v2_14_complexmul.png')

def f15_stn_grid():
    th = np.deg2rad(30); M = np.array([[np.cos(th), -np.sin(th), 0.1], [np.sin(th), np.cos(th), 0]])
    g = np.linspace(-1, 1, 5); G = np.array([[x, y, 1] for y in g for x in g]); S = G @ M.T
    fig, ax = plt.subplots(1, 2, figsize=(11, 4.8))
    ax[0].scatter(G[:, 0], G[:, 1], c='C0'); ax[0].set_title('(a) 输出图的规则网格 $(x_t, y_t)$')
    ax[1].scatter(S[:, 0], S[:, 1], c='C3'); ax[1].set_title('(b) 变换后到输入图中“取像素”的位置 $(x_s, y_s)$\n旋转 30° + 平移 0.1')
    ax[1].scatter([0.5*np.cos(th)+0.1], [0.5*np.sin(th)], s=150, facecolors='none', edgecolors='k', lw=2)
    ax[1].annotate('(0.5,0) → (0.533, 0.25)', xy=(0.533, 0.25), xytext=(0.2, 1.1), arrowprops=dict(arrowstyle='->'))
    ax[0].scatter([0.5], [0], s=150, facecolors='none', edgecolors='k', lw=2)
    for a in ax: a.set_aspect('equal'); a.grid(alpha=.3); a.set_xlim(-1.6, 1.6); a.set_ylim(-1.6, 1.6)
    save(fig, 'v2_15_stn_grid.png')

def f16_pol_example():
    S = np.array([[0.8, 0.1j], [0.1j, -0.6]]); k = np.array([S[0, 0]+S[1, 1], S[0, 0]-S[1, 1], 2*S[0, 1]])/np.sqrt(2)
    fig, ax = plt.subplots(1, 2, figsize=(12, 3.8))
    ax[0].bar(['|HH|', '|HV|', '|VV|'], [0.8, 0.1, 0.6], color=['C0', 'C2', 'C3']); ax[0].set_title('(a) 例题散射矩阵的三个通道幅度')
    ax[1].bar(['$|k_1|^2$ 奇次', '$|k_2|^2$ 偶次', '$|k_3|^2$ 交叉'], np.abs(k)**2, color=['C0', 'C3', 'C2'])
    for i, v in enumerate(np.abs(k)**2): ax[1].text(i, v+.02, f'{v:.2f}', ha='center')
    ax[1].set_title('(b) Pauli 分量功率: 偶次散射占 0.98/1.02 = 96%')
    for a in ax: a.grid(alpha=.3, axis='y')
    save(fig, 'v2_16_pol_example.png')

if __name__ == '__main__':
    for f in [f01_complex, f02_iq, f03_fourier, f04_sampling, f05_barker, f06_doppler_phase, f07_defocus_if, f08_neuron,
              f09_gd, f10_conv, f11_attention, f12_gnn, f13_proto, f14_complexmul, f15_stn_grid, f16_pol_example, f17_stn_affine_fixed]: f()

def f17_stn_affine_fixed():
    """v1 图 A16 的修正版: 剪切子图标题原误写为 CvPGT, 应为论文 5 (REMI) 的 MH-STN。输出 v2_A16_stn_affine.png, 不覆盖 v1 文件。"""
    import make_figures as mf
    mf.save = lambda fig, name: save(fig, 'v2_A16_stn_affine.png')
    src = open(mf.__file__).read()
    assert "剪切 (CvPGT 约束中去掉)" in src
    import types
    code = src[src.index('def fig_stn():'):src.index('# ---------------------------------------------------------------- 卷积')]
    code = code.replace('剪切 (CvPGT 约束中去掉)', '剪切 (论文 5 MH-STN 中去掉)')
    ns = dict(mf.__dict__); exec(code, ns); ns['fig_stn']()
