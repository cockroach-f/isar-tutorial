# -*- coding: utf-8 -*-
"""生成教学动画 (matplotlib + ffmpeg) -> ../videos/*.mp4
用法: python make_videos.py [v1 v2 v3 v4]"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.patches import Polygon, Circle, FancyArrowPatch
import isar_core as ic
ic.setup_cjk_font()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'videos'); os.makedirs(OUT, exist_ok=True)
FPS = 15

def writer(): return FFMpegWriter(fps=FPS, codec='libx264', bitrate=2500, extra_args=['-pix_fmt', 'yuv420p'])

def caption(fig):
    return fig.text(0.5, 0.025, '', ha='center', va='bottom', fontsize=15, color='white',
                    bbox=dict(fc='black', alpha=0.75, boxstyle='round,pad=0.4'))

# ------------------------------------------------------------ V1 转台 -> 多普勒 -> ISAR
def v1():
    fc, B, Nf, dth, Np = 10e9, 1e9, 256, 5.0, 256
    pts, sig = ic.satellite_points('sat_a'); pts = ic.rotate_pts(pts, np.deg2rad(25))
    S, f, th = ic.echo_turntable(pts, sig, fc, B, Nf, dth, Np)
    hr = ic.range_profiles(S); hrdb = ic.to_db(hr, 40)
    r, a, rr, _ = ic.axes_rd(fc, B, Nf, dth, Np)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.suptitle('动画1  转台模型: 目标转动 → 多普勒 → 距离-多普勒 (RD) ISAR 像', fontsize=17)
    ax0 = fig.add_axes([0.03, 0.17, 0.30, 0.68]); ax1 = fig.add_axes([0.38, 0.17, 0.27, 0.68]); ax2 = fig.add_axes([0.71, 0.17, 0.27, 0.68])
    cap = caption(fig)
    # 几何: 为可见, 角度放大显示 (演示用 ×6)
    ax0.set_xlim(-7, 7); ax0.set_ylim(-7, 9); ax0.set_aspect('equal'); ax0.set_title('目标几何 (转角放大显示)')
    ax0.add_patch(Polygon([[-0.5, 8.6], [0.5, 8.6], [0, 7.8]], color='k')); ax0.text(0.7, 8.1, '雷达')
    ax0.annotate('', xy=(0, 5.5), xytext=(0, 7.6), arrowprops=dict(arrowstyle='->', color='gray'))
    sc = ax0.scatter(pts[:, 0], pts[:, 1], s=12, c='C0')
    hl = ax0.scatter([pts[30, 0]], [pts[30, 1]], s=60, c='r', zorder=5)
    ax0.set_xlabel('x / m'); ax0.set_ylabel('y (视线) / m')
    im1 = ax1.imshow(np.full_like(hrdb, -40), origin='lower', aspect='auto', cmap='jet', vmin=-40, vmax=0,
                     extent=[r[0], r[-1], 0, Np]); ax1.set_xlim(-8, 8)
    ax1.set_title('HRRP 历程 (逐脉冲距离压缩)'); ax1.set_xlabel('距离 / m'); ax1.set_ylabel('脉冲序号')
    im2 = ax2.imshow(np.full((Nf, Np), -40.), origin='lower', aspect='auto', cmap='jet', vmin=-40, vmax=0,
                     extent=[-8, 8, r[0], r[-1]]); ax2.set_ylim(-8, 8)
    ax2.set_title('RD 像 (对已有脉冲做方位 FFT)'); ax2.set_xlabel('横向距离 / m'); ax2.set_ylabel('距离 / m')
    ttl2 = ax2.text(0.02, 0.97, '', transform=ax2.transAxes, color='w', va='top', fontsize=11)
    T1, T2, T3 = 6 * FPS, 22 * FPS, 10 * FPS          # 引言 / 积累 / 总结
    total = T1 + T2 + T3
    w = writer()
    with w.saving(fig, os.path.join(OUT, 'V1_turntable_to_isar.mp4'), dpi=100):
        for k in range(total):
            if k < T1:
                ang = 0.0; n = 0
                cap.set_text('平动补偿后, 目标可看作绕中心转动; 雷达沿视线(y)测距离')
            elif k < T1 + T2:
                n = int(np.ceil((k - T1 + 1) / T2 * Np)); ang = th[n - 1] * 6
                cap.set_text(['每发一个脉冲 → 得到一条一维距离像 (HRRP)',
                              '转动使不同横向位置 x 的点产生不同多普勒 f_d = 2ωx/λ',
                              '对慢时间做 FFT: 多普勒 → 横向坐标; 转角越大, 横向越清晰'][min(2, 3 * (k - T1) // T2)])
            else:
                n = Np; ang = th[-1] * 6
                cap.set_text(f'最终: 距离分辨率 c/2B = {rr*100:.0f} cm, 横向分辨率 λ/(2Δθ) ≈ 17 cm (B=1 GHz, Δθ=5°)')
            p = ic.rotate_pts(pts, ang); sc.set_offsets(p); hl.set_offsets(p[30:31])
            if n > 0:
                d = np.full_like(hrdb, -40); d[:n] = hrdb[:n]; im1.set_data(d)
                img = ic.rd_image(S[:n] if n > 4 else S[:4])
                # 横向轴: 只有 n 个脉冲时, 横向窗口不变而分辨率变粗 => 补零到 Np 以保持坐标
                Sp = np.zeros_like(S); Sp[:n] = S[:n]
                hrp = ic.range_profiles(Sp); wv = np.zeros(Np); wv[:n] = np.hanning(n)
                img = np.fft.fftshift(np.fft.ifft(hrp * wv[:, None], axis=0, n=Np), axes=0)
                a_n = (np.arange(Np) - Np/2) * (3e8/fc) / (2 * np.deg2rad(dth))
                im2.set_data(ic.to_db(img, 40).T); im2.set_extent([a_n[0], a_n[-1], r[0], r[-1]]); ax2.set_xlim(-8, 8)
                ttl2.set_text(f'已积累转角 {dth*n/Np:.2f}°')
            w.grab_frame()
    plt.close(fig); print('V1 done')

# ------------------------------------------------------------ V2 脉冲压缩
def v2():
    fs, T = 400e6, 4e-6
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.suptitle('动画2  脉冲压缩: 匹配滤波把长 LFM 脉冲“压”成窄峰', fontsize=17)
    ax1 = fig.add_axes([0.07, 0.58, 0.88, 0.28]); ax2 = fig.add_axes([0.07, 0.17, 0.52, 0.30]); ax3 = fig.add_axes([0.66, 0.17, 0.29, 0.30])
    cap = caption(fig)
    d = 3.0
    # Part 1: 滑动相关 (B = 100 MHz)
    B = 100e6; t, ref, k = ic.lfm(T, B, fs)
    N = 3000; tau1 = 900; tau2 = tau1 + int(round(2*d/3e8*fs))
    x = np.zeros(N, complex); x[tau1:tau1+len(ref)] += ref; x[tau2:tau2+len(ref)] += 0.7*ref
    y = ic.matched_filter(x, ref); ya = np.abs(y)/np.abs(y).max()
    rng_ax = (np.arange(N) - tau1) / fs * 3e8 / 2
    ax1.plot(rng_ax, x.real, lw=.5, color='C0'); refl, = ax1.plot([], [], color='C3', lw=.8, alpha=.8)
    ax1.set_xlim(rng_ax[0], rng_ax[-1]); ax1.set_ylim(-2, 2); ax1.set_title('接收回波 (两目标相距 3 m, 波形完全重叠) 与 滑动的参考信号(红)')
    ax1.set_xlabel('距离 / m')
    ln, = ax2.plot([], [], 'C2'); ax2.set_xlim(rng_ax[0], rng_ax[-1]); ax2.set_ylim(0, 1.1)
    ax2.set_title('匹配滤波输出 |y| (相关值)'); ax2.set_xlabel('距离 / m')
    ln3, = ax3.plot([], [], 'C2'); ax3.set_xlim(-6, 10); ax3.set_ylim(0, 1.1); ax3.set_title('放大: 0 ~ 3 m 附近'); ax3.set_xlabel('距离 / m')
    ax3.axvline(0, color='gray', ls=':'); ax3.axvline(d, color='gray', ls=':')
    P1 = 18 * FPS; P2 = 14 * FPS
    w = writer()
    with w.saving(fig, os.path.join(OUT, 'V2_pulse_compression.mp4'), dpi=100):
        for kf in range(P1):
            n = int(kf / (P1 - 1) * (N - 1))
            lo = max(0, n - len(ref) + 1) if False else n
            seg = np.arange(n, min(N, n + len(ref)))
            refl.set_data(rng_ax[seg], ref[:len(seg)].real * 1.0)
            ln.set_data(rng_ax[:n+1], ya[:n+1]); ln3.set_data(rng_ax[:n+1], ya[:n+1])
            cap.set_text(['参考信号在回波上滑动, 每个位置计算一次“相似度”',
                          '对齐的瞬间, 所有频率成分同相叠加 → 尖峰',
                          '右侧放大图: 两个尖峰分开 → 原本重叠的两个目标被分辨出来'][min(2, 3 * kf // P1)])
            w.grab_frame()
        # Part 2: 带宽扫描
        ax1.cla(); ax1.set_title('改变带宽 B: 主瓣宽度 ≈ c/2B'); ax1.axis('off')
        txt = ax1.text(0.5, 0.5, '', ha='center', va='center', fontsize=22, transform=ax1.transAxes)
        ax3.remove(); ax2.set_position([0.07, 0.17, 0.88, 0.30]); ax2.cla(); ax2.set_xlim(-6, 10); ax2.set_ylim(0, 1.1); ax2.set_xlabel('距离 / m'); ax2.set_title('匹配滤波输出 (两目标相距 3 m)')
        ax2.axvline(0, color='gray', ls=':'); ax2.axvline(d, color='gray', ls=':')
        ln2, = ax2.plot([], [], 'C2', lw=1.5)
        Bs = np.geomspace(15e6, 300e6, P2)
        for kf, Bk in enumerate(Bs):
            t, ref, k = ic.lfm(T, Bk, fs)
            x = np.zeros(N, complex); x[tau1:tau1+len(ref)] += ref; x[tau2:tau2+len(ref)] += 0.7*ref
            y = np.abs(ic.matched_filter(x, ref)); y /= y.max()
            ln2.set_data(rng_ax, y)
            txt.set_text(f'B = {Bk/1e6:.0f} MHz      距离分辨率 c/2B = {3e8/2/Bk:.2f} m')
            cap.set_text('带宽越大, 峰越窄; 分辨率 < 3 m 时两目标才能分开' if Bk < 50e6 else '带宽越大, 峰越窄 —— 太赫兹雷达 (10 GHz 带宽) 可达 1.5 cm')
            w.grab_frame()
        for _ in range(3 * FPS): w.grab_frame()
    plt.close(fig); print('V2 done')

# ------------------------------------------------------------ V3 少样本 episode
def v3():
    kinds = ['sat_a', 'sat_b', 'sat_c', 'sat_d', 'plane']
    rng = np.random.default_rng(7)
    def img(k, az, seed):
        pts, sig = ic.satellite_points(k, seed=kinds.index(k))
        S, _, _ = ic.echo_turntable(ic.rotate_pts(pts, np.deg2rad(az)), sig, 10e9, 1e9, 96, 5.0, 96, snr_db=20, seed=seed)
        return ic.to_db(ic.rd_image(S)).T[14:82, 14:82]
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.suptitle('动画3  少样本学习的一个任务 (3-way 1-shot) 与原型网络推理', fontsize=17)
    cap = caption(fig)
    emb = fig.add_axes([0.52, 0.17, 0.44, 0.68]); emb.set_xlim(-4, 4); emb.set_ylim(-4, 4); emb.set_title('嵌入空间 (示意)'); emb.grid(alpha=.3)
    w = writer()
    with w.saving(fig, os.path.join(OUT, 'V3_fewshot_episode.mp4'), dpi=100):
        for ep in range(2):
            cls = rng.choice(5, 3, replace=False); qc = rng.integers(3)
            sup = [img(kinds[c], rng.uniform(0, 360), ep*10+i) for i, c in enumerate(cls)]
            qimg = img(kinds[cls[qc]], rng.uniform(0, 360), 99+ep)
            centers = np.array([[-2.2, 1.8], [2.2, 2.0], [0.0, -2.4]]) + rng.normal(0, .3, (3, 2))
            qpos = centers[qc] + np.array([0.9, -0.6])
            axs = [fig.add_axes([0.03 + 0.15*i, 0.55, 0.13, 0.26]) for i in range(3)]
            axq = fig.add_axes([0.18, 0.18, 0.13, 0.26])
            for a in axs + [axq]: a.set_xticks([]); a.set_yticks([]); a.set_visible(False)
            arts = []
            steps = [(3, f'第 {ep+1} 个任务: 从类别池中随机抽 3 类, 每类只给 1 张带标签的“支持图”'),
                     (3, '把支持图送入同一个特征提取网络 f(·), 映射成嵌入空间中的点'),
                     (2, '每类支持嵌入的平均值 = 该类“原型” (K=1 时就是它本身)'),
                     (3, '来了一张未知的“查询图”, 同样映射到嵌入空间'),
                     (3, '计算到每个原型的距离, softmax(−距离) 得到各类概率'),
                     (2, f'距离最近 → 判为 类别 {qc+1}; 训练时用此误差更新 f(·)')]
            for si, (sec, txt) in enumerate(steps):
                for fr in range(sec * FPS):
                    cap.set_text(txt)
                    if si == 0 and fr == 0:
                        for i, a in enumerate(axs):
                            a.set_visible(True); a.imshow(sup[i], origin='lower', cmap='jet', vmin=-40, vmax=0)
                            a.set_title(f'类别 {i+1} 支持图', color=f'C{i}', fontsize=11)
                            for s in a.spines.values(): s.set_edgecolor(f'C{i}'); s.set_linewidth(3)
                    if si == 1 and fr == 0:
                        for i in range(3): arts.append(emb.scatter(*centers[i], s=120, c=f'C{i}', edgecolors='k', zorder=3))
                    if si == 2 and fr == 0:
                        for i in range(3):
                            arts.append(emb.scatter(*centers[i], s=600, marker='*', c=f'C{i}', edgecolors='k', zorder=4))
                            arts.append(emb.text(centers[i][0]+.3, centers[i][1]+.3, f'原型 {i+1}', fontsize=11))
                    if si == 3 and fr == 0:
                        axq.set_visible(True); axq.imshow(qimg, origin='lower', cmap='jet', vmin=-40, vmax=0)
                        axq.set_title('查询图 (类别未知)', fontsize=11)
                        for s in axq.spines.values(): s.set_edgecolor('k'); s.set_linewidth(3)
                        arts.append(emb.scatter(*qpos, s=200, marker='X', c='k', zorder=5))
                    if si == 4 and fr == 0:
                        dd = np.linalg.norm(centers - qpos, axis=1); p = np.exp(-dd*1.5); p /= p.sum()
                        for i in range(3):
                            arts.append(emb.plot(*np.stack([qpos, centers[i]]).T, '--', color=f'C{i}', lw=2)[0])
                            arts.append(emb.text(*(qpos + centers[i]) / 2, f'd={dd[i]:.1f}\np={p[i]:.2f}', fontsize=10,
                                                 bbox=dict(fc='w', alpha=.8)))
                    if si == 5 and fr == 0:
                        arts.append(emb.add_patch(Circle(qpos, 0.45, fill=False, ec=f'C{qc}', lw=3)))
                    w.grab_frame()
            for a in arts: a.remove()
            for a in axs + [axq]: a.remove()
        cap.set_text('训练: 在“基类”上反复抽任务; 测试: 在从未见过的“新类”上抽任务评估')
        for _ in range(4 * FPS): w.grab_frame()
    plt.close(fig); print('V3 done')

# ------------------------------------------------------------ V4 散焦
def v4():
    fc, B, Nf, dth, Np = 10e9, 1e9, 256, 5.0, 256
    pts, sig = ic.satellite_points('sat_a'); pts = ic.rotate_pts(pts, np.deg2rad(25))
    r, a, _, _ = ic.axes_rd(fc, B, Nf, dth, Np)
    fig = plt.figure(figsize=(12.8, 7.2), dpi=100)
    fig.suptitle('动画4  非匀速转动 (角加速度) 导致的方位散焦', fontsize=17)
    ax0 = fig.add_axes([0.07, 0.2, 0.36, 0.62]); ax1 = fig.add_axes([0.55, 0.2, 0.40, 0.62])
    cap = caption(fig)
    u = np.linspace(-0.5, 0.5, Np)
    l1, = ax0.plot(u, dth*u, 'k--', label='匀速: θ=ωt'); l2, = ax0.plot([], [], 'r', lw=2, label='加速: θ=ωt+½αt²')
    ax0.set_xlabel('归一化慢时间'); ax0.set_ylabel('转角 θ / °'); ax0.legend(loc='upper left'); ax0.grid(alpha=.3)
    ax0.set_ylim(-3.5, 4.5); ax0.set_title('转角随时间的变化')
    im = ax1.imshow(np.zeros((Nf, Np)), origin='lower', cmap='jet', vmin=-40, vmax=0, aspect='auto',
                    extent=[a[0], a[-1], r[0], r[-1]]); ax1.set_xlim(-8, 8); ax1.set_ylim(-8, 8)
    ax1.set_xlabel('横向距离 / m'); ax1.set_ylabel('距离 / m')
    txt = ax1.text(0.02, 0.97, '', transform=ax1.transAxes, color='w', va='top', fontsize=13)
    al = np.concatenate([np.linspace(0, 1.0, 16 * FPS), np.full(3 * FPS, 1.0), np.linspace(1.0, 0, 5 * FPS)])
    w = writer()
    with w.saving(fig, os.path.join(OUT, 'V4_defocus.mp4'), dpi=100):
        for k, ar in enumerate(al):
            S, _, th = ic.echo_turntable(pts, sig, fc, B, Nf, dth, Np, alpha_ratio=ar)
            img = ic.rd_image(S)
            l2.set_data(u, np.rad2deg(th)); im.set_data(ic.to_db(img).T)
            txt.set_text(f'二次项比例 = {ar:.2f}\n图像熵 = {ic.image_entropy(img):.2f}')
            if k < 16 * FPS: cap.set_text('多普勒 ∝ 转速; 转速在变 → 同一散射点的多普勒随时间漂移 → 横向“拖尾”')
            elif k < 19 * FPS: cap.set_text('散焦像: 熵变大, 细节模糊 —— 论文2 CV-GNN 直接对这类复值散焦像分类')
            else: cap.set_text('运动补偿/自聚焦(如最小熵)的目标: 估计并消除二次相位, 让图像重新聚焦')
            w.grab_frame()
    plt.close(fig); print('V4 done')

if __name__ == '__main__':
    todo = sys.argv[1:] or ['v1', 'v2', 'v3', 'v4']
    for t in todo: globals()[t]()
