# -*- coding: utf-8 -*-
"""入门项目1-步骤2: 用 ResNet18 对仿真 RD 像分类 (CPU 即可运行)
关键实验建议:
  (1) 随机划分 vs 按方位角划分 (--split azimuth): 后者测试“没见过的姿态”, 更接近真实难度;
  (2) 改变训练样本数 (--train_per_class) 观察小样本下精度下降;
  (3) 改变 B / dtheta / SNR 重新生成数据, 观察分辨率与噪声对识别的影响。
运行: python project1_train_resnet18.py --data data/rd_dataset.npz --epochs 15
"""
import argparse, numpy as np, torch, torch.nn as nn, torchvision

def make_model(nc):
    m = torchvision.models.resnet18(weights=None, num_classes=nc)
    m.conv1 = nn.Conv2d(1, 64, 3, 1, 1, bias=False)   # 单通道小图: 3×3 stem, 去掉首个 maxpool
    m.maxpool = nn.Identity()
    return m

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default='data/rd_dataset.npz'); ap.add_argument('--epochs', type=int, default=15)
    ap.add_argument('--split', choices=['random', 'azimuth'], default='random')
    ap.add_argument('--train_per_class', type=int, default=0, help='>0 时每类只用这么多张训练')
    ap.add_argument('--train_az_max', type=float, default=250, help='azimuth 划分时, 训练用 [0, train_az_max) 度, 测试用 [test_az_min, 360)')
    ap.add_argument('--test_az_min', type=float, default=250)
    ap.add_argument('--flip', action='store_true', help='训练时随机横向翻转')
    ap.add_argument('--bs', type=int, default=32); ap.add_argument('--lr', type=float, default=1e-3)
    a = ap.parse_args(); torch.manual_seed(0); rng = np.random.default_rng(0)
    d = np.load(a.data); X, y, az = d['X'], d['y'], d['az']
    if a.split == 'random':
        idx = rng.permutation(len(y)); ntr = int(0.7 * len(y)); tr, te = idx[:ntr], idx[ntr:]
    else:   # 默认 方位角 0-250° 训练, 250-360° 测试: 测试姿态从未见过
        tr, te = np.nonzero(az < a.train_az_max)[0], np.nonzero(az >= a.test_az_min)[0]
    if a.train_per_class > 0:
        tr = np.concatenate([rng.permutation(tr[y[tr] == c])[:a.train_per_class] for c in np.unique(y)])
    Xtr, ytr = torch.tensor(X[tr]), torch.tensor(y[tr]); Xte, yte = torch.tensor(X[te]), torch.tensor(y[te])
    m = make_model(int(y.max()) + 1); opt = torch.optim.AdamW(m.parameters(), a.lr, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.epochs); lossf = nn.CrossEntropyLoss()
    print(f'train {len(tr)}  test {len(te)}  split={a.split}', flush=True)
    for ep in range(a.epochs):
        m.train(); perm = torch.randperm(len(ytr)); tot = 0
        for i in range(0, len(perm), a.bs):
            b = perm[i:i + a.bs]; xb = Xtr[b]
            if a.flip and torch.rand(1) < 0.5: xb = torch.flip(xb, [3])   # 可选增强: 横向翻转
            loss = lossf(m(xb), ytr[b]); opt.zero_grad(); loss.backward(); opt.step(); tot += loss.item() * len(b)
        sched.step(); m.eval()
        with torch.no_grad(): acc = (m(Xte).argmax(1) == yte).float().mean().item()
        print(f'epoch {ep+1:2d}  loss {tot/len(ytr):.3f}  test acc {acc*100:.2f}%', flush=True)

if __name__ == '__main__':
    main()
