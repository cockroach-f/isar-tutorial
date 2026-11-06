# -*- coding: utf-8 -*-
"""入门项目1-步骤1: 用点散射体仿真生成一个小型 ISAR 分类数据集
  - 类别: random_target(0..C-1) 生成的 C 种“卫星”
  - 每类 n 张, 方位角在 [0,360) 随机, 加高斯噪声
  - 保存为 data/rd_dataset.npz (X: [N,1,64,64] float32, y: [N])
运行: python project1_rd_dataset.py --classes 6 --per_class 120
"""
import argparse, os, numpy as np
import isar_core as ic

def build(C=6, n=120, N=64, B=1e9, dtheta=5.0, snr=15, seed=0):
    rng = np.random.default_rng(seed)
    X, y, az = [], [], []
    for c in range(C):
        pts, sig = ic.random_target(c)
        for i in range(n):
            a = rng.uniform(0, 360)
            X.append(ic.simulate_image(pts, sig, a, B=B, N=N, dtheta=dtheta, snr_db=snr, seed=int(rng.integers(1 << 30))))
            y.append(c); az.append(a)
    return np.stack(X)[:, None], np.array(y), np.array(az)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--classes', type=int, default=6); ap.add_argument('--per_class', type=int, default=120)
    ap.add_argument('--size', type=int, default=64); ap.add_argument('--snr', type=float, default=15)
    ap.add_argument('--B', type=float, default=1e9, help='带宽 Hz'); ap.add_argument('--dtheta', type=float, default=5.0, help='积累角 度')
    ap.add_argument('--out', default='data/rd_dataset.npz')
    a = ap.parse_args()
    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    X, y, az = build(a.classes, a.per_class, a.size, B=a.B, dtheta=a.dtheta, snr=a.snr)
    np.savez_compressed(a.out, X=X, y=y, az=az)
    print('saved', a.out, X.shape, np.bincount(y))
