# -*- coding: utf-8 -*-
"""
dbssit_lite.py —— DB-SSIT 思想的【教学简化版】(非官方代码, 非论文原始结构的复现!)
参考: W. Chen et al., "Terahertz Polarimetric ISAR Target Recognition Based on a Dual-Branch
Spatial-Scatter Interaction Transformer", Electromagnetic Science, 2025.
简化要点 (与原文的差异):
  * 原文 4 个层级 stage、PSFEB 含“极坐标注意力(PCA)+ECA”、LGFB 含 E-MHSA + MHCA + LFFN;
    这里只保留骨架: 6维极化特征 -> MixConv 预处理 -> [极化散射分支 | 空间分支] -> 简化 Transformer 融合 -> 分类
  * 极化分支: 分组卷积(每组对应一种极化特征) + 1×1 交互卷积 + 沿 X/Y 方向的均值/方差池化注意力(仿 PCA 思想)
  * 空间分支: 卷积 + 深度卷积 + 空间注意力 (avg/max 沿通道)
用途: 理解结构、在自己的数据上做基线; 结果不能当作论文结果引用。
"""
import torch, torch.nn as nn, torch.nn.functional as F

class MixConvPre(nn.Module):
    """6维特征 -> 3组(3×3/5×5/7×7) 每组2通道输入 -> 32 通道 -> BN -> MaxPool -> 1×1 -> 6 -> 1×1 -> 3 (与原文 Fig.2 描述一致的通道流)"""
    def __init__(self, out=32):
        super().__init__()
        self.convs = nn.ModuleList([nn.Conv2d(2, out // 4 if k != 3 else out // 2, k, padding=k // 2) for k in (3, 5, 7)])
        self.bn = nn.BatchNorm2d(out); self.pool = nn.MaxPool2d(2)
        self.p1 = nn.Conv2d(out, 6, 1); self.p2 = nn.Conv2d(6, 3, 1)
    def forward(self, x):                        # x: [B,6,H,W]
        y = torch.cat([c(x[:, 2*i:2*i+2]) for i, c in enumerate(self.convs)], 1)
        return self.p2(self.p1(self.pool(F.relu(self.bn(y)))))

class PolarAxisAttention(nn.Module):
    """仿“极坐标注意力”思想: 沿 X / Y 的均值与方差统计 -> 两个方向的注意力权重"""
    def __init__(self, c):
        super().__init__()
        self.f = nn.Sequential(nn.Conv2d(2*c, c, 1, groups=c), nn.BatchNorm2d(c), nn.ReLU())
        self.gx = nn.Conv2d(c, c, 1); self.gy = nn.Conv2d(c, c, 1)
    def forward(self, x):
        B, C, H, W = x.shape
        xm, xv = x.mean(3, keepdim=True), x.var(3, keepdim=True)              # [B,C,H,1]
        ym, yv = x.mean(2, keepdim=True), x.var(2, keepdim=True)              # [B,C,1,W]
        sx = torch.stack([xm, xv], 2).flatten(1, 2)                            # [B,2C,H,1]
        sy = torch.stack([ym, yv], 2).flatten(1, 2).transpose(2, 3)            # [B,2C,W,1]
        z = self.f(torch.cat([sx, sy], 2))
        ax, ay = torch.split(z, [H, W], 2)
        return x * torch.sigmoid(self.gx(ax)) * torch.sigmoid(self.gy(ay.transpose(2, 3)))

class PolBranch(nn.Module):
    def __init__(self, cin, c, groups=3):
        super().__init__()
        self.g = nn.Conv2d(cin, c, 3, padding=1, groups=groups)    # 每组 ≈ 一种极化模式
        self.inter = nn.Conv2d(c, c, 1)                             # 交互卷积: 跨极化通道混合
        self.att = PolarAxisAttention(c); self.bn = nn.BatchNorm2d(c)
    def forward(self, x): return F.gelu(self.bn(self.att(self.inter(self.g(x)))))

class SpatialBranch(nn.Module):
    def __init__(self, cin, c):
        super().__init__()
        self.c1 = nn.Conv2d(cin, c, 3, padding=1); self.dw = nn.Conv2d(c, c, 3, padding=1, groups=c); self.c2 = nn.Conv2d(c, c, 3, padding=1)
        self.sa = nn.Sequential(nn.Conv2d(2, 1, 7, padding=3), nn.Sigmoid()); self.bn = nn.BatchNorm2d(c)
    def forward(self, x):
        y = self.c2(F.relu(self.dw(F.relu(self.c1(x)))))
        a = self.sa(torch.cat([y.mean(1, keepdim=True), y.amax(1, keepdim=True)], 1))
        return F.leaky_relu(self.bn(y * a), 0.01)

class Stage(nn.Module):
    def __init__(self, cin, c, stride):
        super().__init__()
        self.embed = nn.Conv2d(cin, cin, stride, stride) if stride > 1 else nn.Identity()   # patch embedding (下采样)
        self.pol = PolBranch(cin, c, groups=3 if cin % 3 == 0 and c % 3 == 0 else 1); self.spa = SpatialBranch(cin, c)
        self.fuse = nn.Conv2d(2 * c, c, 1)
    def forward(self, x):
        x = self.embed(x); return self.fuse(torch.cat([self.pol(x), self.spa(x)], 1))

class LGFBLite(nn.Module):
    """局部-全局融合: K/V 先平均池化的“高效”多头自注意力 + 深度卷积 FFN"""
    def __init__(self, c, heads=4, sr=2):
        super().__init__()
        self.q = nn.Conv2d(c, c, 1); self.kv = nn.Conv2d(c, 2 * c, 1); self.sr = nn.AvgPool2d(sr); self.h = heads
        self.proj = nn.Conv2d(c, c, 1); self.n1 = nn.BatchNorm2d(c); self.n2 = nn.BatchNorm2d(c)
        self.ffn = nn.Sequential(nn.Conv2d(c, c, 3, padding=1, groups=c), nn.ReLU(), nn.Conv2d(c, c, 1))
    def forward(self, x):
        B, C, H, W = x.shape; y = self.n1(x)
        q = self.q(y).reshape(B, self.h, C // self.h, H * W).transpose(2, 3)
        k, v = self.kv(self.sr(y)).reshape(B, 2, self.h, C // self.h, -1).unbind(1)
        att = torch.softmax(q @ k / (C // self.h) ** 0.5, -1)                      # [B,h,HW,hw]
        o = (att @ v.transpose(2, 3)).transpose(2, 3).reshape(B, C, H, W)
        x = x + self.proj(o)
        return x + self.ffn(self.n2(x))

class DBSSITLite(nn.Module):
    def __init__(self, num_classes=6, widths=(24, 48, 96, 192)):
        super().__init__()
        self.pre = MixConvPre(); cin = 3; st = []
        for i, w in enumerate(widths):
            st.append(Stage(cin, w, 2 if i > 0 else 1)); cin = w
        self.stages = nn.Sequential(*st); self.lgfb = LGFBLite(cin)
        self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.BatchNorm1d(cin), nn.Linear(cin, num_classes))
    def forward(self, x6): return self.head(self.lgfb(self.stages(self.pre(x6))))

def pol_features_torch(HH, HV, VV, win=3):
    """由复数 HH/HV/VV [B,H,W] 计算 6 维特征 (按论文式 4-9, D 采用论文印刷形式)。"""
    k = torch.stack([HH + VV, HH - VV, 2 * HV], 1) / 2 ** 0.5           # [B,3,H,W] complex
    def avg(t): return torch.complex(F.avg_pool2d(t.real, win, 1, win // 2), F.avg_pool2d(t.imag, win, 1, win // 2))
    T = lambda i, j: avg((k[:, i] * k[:, j].conj()).unsqueeze(1)).squeeze(1)
    T11, T22, T33 = T(0, 0).real, T(1, 1).real, T(2, 2).real; e = 1e-8; span = T11 + T22 + T33 + e
    f = [10 * torch.log10(span), T22 / span, T33 / span, T(0, 1).abs() / (T11 * T33 + e).sqrt(),
         T(0, 2).abs() / (T11 * T33 + e).sqrt(), T(1, 2).abs() / (T33 * T22 + e).sqrt()]
    return torch.stack(f, 1)

if __name__ == '__main__':
    m = DBSSITLite(6); x = torch.randn(2, 6, 128, 128)
    print('输出形状', m(x).shape, ' 参数量 %.2fM' % (sum(p.numel() for p in m.parameters()) / 1e6))
    HH = torch.randn(2, 128, 128, dtype=torch.cfloat); print('6维特征', pol_features_torch(HH, HH * 0.1, -HH).shape)
