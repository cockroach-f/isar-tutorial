# -*- coding: utf-8 -*-
"""入门项目2: 原型网络 (Prototypical Network) 做 ISAR 少样本识别 —— 完整的 episode 训练/测试流程
  - 基类: random_target(0..19)  (20 类, 用于元训练)
  - 新类: random_target(100..109) (10 类, 训练时从未出现, 只用于测试)
  - 每个 episode: N-way K-shot, 每类 Q 个查询
运行: python project2_protonet.py --way 5 --shot 1 --episodes 1500
"""
import argparse, numpy as np, torch, torch.nn as nn, torch.nn.functional as F
import isar_core as ic

def gen_pool(cids, n, N=48, seed=0):
    rng = np.random.default_rng(seed); pool = {}
    for c in cids:
        pts, sig = ic.random_target(c)
        pool[c] = np.stack([ic.simulate_image(pts, sig, rng.uniform(0, 360), N=N, snr_db=15,
                                              seed=int(rng.integers(1 << 30))) for _ in range(n)])[:, None]
    return pool

def conv4():
    def blk(i, o): return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(), nn.MaxPool2d(2))
    return nn.Sequential(blk(1, 64), blk(64, 64), blk(64, 64), blk(64, 64), nn.Flatten())

def episode(pool, way, shot, q, rng):
    cls = rng.choice(list(pool), way, replace=False); s, qq = [], []
    for c in cls:
        idx = rng.permutation(len(pool[c]))[:shot + q]; s.append(pool[c][idx[:shot]]); qq.append(pool[c][idx[shot:]])
    s = torch.tensor(np.concatenate(s)); qq = torch.tensor(np.concatenate(qq))
    yq = torch.arange(way).repeat_interleave(q)
    return s, qq, yq

def proto_logits(f, s, qx, way, shot):
    zs = f(s).view(way, shot, -1).mean(1)          # 原型 = 支持嵌入均值
    zq = f(qx)
    return -torch.cdist(zq, zs) ** 2               # 负平方欧氏距离作为 logits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--way', type=int, default=5); ap.add_argument('--shot', type=int, default=1)
    ap.add_argument('--query', type=int, default=10); ap.add_argument('--episodes', type=int, default=1500)
    ap.add_argument('--per_class', type=int, default=60); ap.add_argument('--test_episodes', type=int, default=300)
    a = ap.parse_args(); torch.manual_seed(0); rng = np.random.default_rng(0)
    print('生成数据 (基类 20, 新类 10) ...')
    base = gen_pool(range(20), a.per_class, seed=1); novel = gen_pool(range(100, 110), a.per_class, seed=2)
    f = conv4(); opt = torch.optim.Adam(f.parameters(), 1e-3)
    def evaluate(n):
        f.eval(); accs = []
        with torch.no_grad():
            for _ in range(n):
                s, qx, yq = episode(novel, a.way, a.shot, a.query, rng)
                accs.append((proto_logits(f, s, qx, a.way, a.shot).argmax(1) == yq).float().mean().item())
        f.train(); accs = np.array(accs)
        return accs.mean() * 100, 1.96 * accs.std() / np.sqrt(n) * 100
    m0, c0 = evaluate(100); print(f'训练前 (随机网络) 新类 {a.way}-way {a.shot}-shot: {m0:.2f} ± {c0:.2f}%')
    for ep in range(1, a.episodes + 1):
        s, qx, yq = episode(base, a.way, a.shot, a.query, rng)
        loss = F.cross_entropy(proto_logits(f, s, qx, a.way, a.shot), yq)
        opt.zero_grad(); loss.backward(); opt.step()
        if ep % 250 == 0:
            m, c = evaluate(100); print(f'episode {ep}  loss {loss.item():.3f}  新类精度 {m:.2f} ± {c:.2f}%', flush=True)
    m, c = evaluate(a.test_episodes); print(f'最终: 新类 {a.way}-way {a.shot}-shot 精度 {m:.2f} ± {c:.2f}% (95% 置信区间)')

if __name__ == '__main__':
    main()
