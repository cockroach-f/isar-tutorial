# 附录 A 代码、图与视频清单

所有文件位于 `/workspace/isar-tutorial/` 下。依赖：Python 3、numpy、scipy、matplotlib、ffmpeg；项目代码另需 PyTorch 与 torchvision（CPU 版即可）。

| 文件 | 作用 |
|---|---|
| `code/isar_core.py` | 核心仿真库：点散射体目标、转台回波、HRRP、RD 成像、LFM 与匹配滤波、极化（典型散射矩阵、Pauli、6 维特征、简缩极化）、散射中心提取与 kNN 构图、参数化随机目标 |
| `code/make_figures.py` | 生成 Part A 的仿真图（`figures/A01–A20`） |
| `code/make_figures_v2.py` | 第 2 版新增的基础概念例题配图（`figures/v2_01–v2_16`），以及修正了子图标题的 `v2_A16_stn_affine.png`（v1 图 A16 中“剪切”子图误标为 CvPGT，应为论文 5 的 MH-STN） |
| `code/make_diagrams.py` | 生成 7 篇论文的自绘简化框图、分类体系图与阅读路线图（`figures/B1–B7`、`C1`、`C2`） |
| `code/make_videos.py` | 生成 4 段动画（`videos/V1–V4`） |
| `code/extract_paper_figs.py`、`code/fix_paper_figs.py` | 从论文 PDF 中按图题自动裁剪原文图（`paper_figs/`），后者对少数裁剪不准的图做手工修正 |
| `code/project1_rd_dataset.py` | 入门项目 1：生成仿真 RD 数据集 |
| `code/project1_train_resnet18.py` | 入门项目 1：ResNet18 训练与测试（随机划分 / 按方位划分） |
| `code/project2_protonet.py` | 入门项目 2：原型网络少样本识别（基类 / 新类不相交，episode 训练） |
| `code/dbssit_lite.py` | DB-SSIT 思想的教学简化版网络与 6 维极化特征（**非官方代码**） |
| `build/build.py`、`build/style.css` | 由 `chapters/*.md` 生成 HTML 与 PDF |

**视频**

| 文件 | 时长 | 内容 |
|---|---|---|
| `videos/V1_turntable_to_isar.mp4` | 38 s | 转台转动 → HRRP 历程 → RD 像随积累角逐渐清晰 |
| `videos/V2_pulse_compression.mp4` | 35 s | 匹配滤波滑动相关；带宽扫描与分辨率 |
| `videos/V3_fewshot_episode.mp4` | 36 s | 3-way 1-shot 任务与原型网络推理（两个任务） |
| `videos/V4_defocus.mp4` | 24 s | 角加速度增大导致散焦，图像熵变化 |

**表 A-1 入门项目在本机（CPU）上的实测结果**（仿真数据，仅用于说明现象，不代表任何论文结果）

| 项目 | 设置 | 结果 |
|---|---|---|
| 项目 1 | 6 类 × 100 幅，64×64，B = 1 GHz，Δθ = 5°，SNR 15 dB；随机 7:3 划分，ResNet18，8 epoch，随机横向翻转 | 测试精度 100.00% |
| 项目 1 | 同上，按方位划分：0–250° 训练，250–360° 测试，随机横向翻转 | 测试精度 100.00% |
| 项目 1 | 同上，按方位划分：0–90° 训练，180–360° 测试，无翻转 | 测试精度 15.21%（随机猜测为 16.7%） |
| 项目 2 | 基类 20 / 新类 10，每类 40 幅 48×48，Conv4 原型网络，1000 个 episode；5-way 1-shot | 训练前 42.08 ± 1.82%，训练后 91.69 ± 0.97%（300 个测试任务） |
| 项目 2 | 同上，5-way 5-shot | 训练前 60.76 ± 2.01%，训练后 96.43 ± 0.65% |

**怎么理解这些数字？** 二维点散射体模型中，方位角变化基本等价于图像的平面旋转，而且仿真目标结构差异明显、没有遮挡和闪烁，所以只要训练姿态覆盖较广，CNN 就能达到 100%。一旦测试姿态远离训练范围（0–90° → 180–360°），精度就跌到随机猜测水平，直观说明了“姿态敏感”。仿真少样本精度（> 90%）远高于论文 5、6 中的 60–90%，原因同样是仿真过于理想。想得到更接近论文的难度，可以：降低带宽和积累角；加入散焦（`alpha_ratio`）；训练、测试使用不同的成像参数；给散射点加入随角度变化的幅度与遮挡；使用真实数据。

# 附录 B 存疑与未能核实之处汇总

以下内容在对照原文时发现表述不清、前后不一致或无法核实，正文中已用【存疑】标注：

| 论文 | 位置 | 问题 |
|---|---|---|
| 1 | 题目 | 正式题目为 “Dual-Branch **Spatial-Scatter** Interaction Transformer”，并非 “spatial-spectral” |
| 1 | 式 (7) | 特征 D 印刷为 $|T_{12}|/\sqrt{T_{11}T_{33}}$，常见定义为 $\sqrt{T_{11}T_{22}}$ |
| 1 | 式 (12) | 正文称 FFN 使用 GELU，式 (12) 为 ReLU 形式 |
| 1 | 数据划分 | 未说明扩增（至 3024 幅）与 7:2:1 划分的先后顺序，可能存在数据泄漏 |
| 1 | 数据来源 | 称回波为“采集”所得，未说明是否为缩比模型实测；“平均加权策略”细节不明；类别名称未给出 |
| 2 | Table II | 称“随机选 5 类、每类 20 个样本训练”，但给出 8 类 + 实测共 9 列精度；数据集部分又称“每类 30 幅训练”；评测协议不清 |
| 2 | Table I | 转动加速度 5000 rad/s² 为原文印刷值，数值偏大，未能核实 |
| 2 | 代码 | 原文称代码将公开于 github.com/yhx-hit/cv_gnn，未核实可用性 |
| 3 | 式 (6) | 能量归一化公式的抽取形式不清 |
| 3 | Table III | 正文称该表显示 RAM 对 ResNet50 的提升，但表中无 ResNet50 相关行 |
| 3 | XGBoost 参数 | “ESR 0.8” 含义未说明 |
| 3 | Fig. 14 | 特征得分方差（132.8 vs 36.8）与正文“更集中”的解读方向不完全一致 |
| 4 | Fig. 9 结论 | “最小步长至少为 32° 和 12°” 措辞有歧义（逻辑上应为步长上限） |
| 4 | Table XII 结论 | 称 5-shot 提升 5.58–12.49%，但相对 GNN（62.35%）的提升应为 13.92% |
| 5 | 式 (15) | 印刷为 $\mathrm{MLP}(v_i - v_j)$，按上下文应为绝对值 |
| 5 | Table VIII | 列标题有一处重复印刷（两列都写为 MH-STN+Conv4） |
| 6 | 式 (34) | 损失权重 $\lambda_1$–$\lambda_4$ 的取值未在正文中找到 |
| 6 | 数据集 | “每个站获得 90 幅图像”未说明是否按卫星 / 参数组合计 |

此外：

- 本文所有“自绘”框图是对原文的简化理解，模块细节以原文为准；
- `dbssit_lite.py` 不是原文代码，结构上做了大幅简化；
- 仿真图使用理想点散射模型，未包含真实电磁散射、遮挡与噪声特性。

# 附录 C 参考文献

1. W. Chen, Y. Li, J. Fu, H. Wang, M. Xing, Y. Zhu, G. Fang, “Terahertz polarimetric ISAR target recognition based on a dual-branch spatial-scatter interaction transformer,” *Electromagnetic Science*, 2025, doi: 10.23919/emsci.2025.0060.
2. Y. Zhang, H. Yuan, H. Li, C. Wei, C. Yao, “Complex-valued graph neural network on space target classification for defocused ISAR images,” *IEEE Geosci. Remote Sens. Lett.*, vol. 19, Art. no. 4512905, 2022, doi: 10.1109/LGRS.2022.3185709.
3. Y. Zhang, H. Yuan, H. Li, J. Chen, M. Niu, “Meta-learner-based stacking network on space target recognition for ISAR images,” *IEEE J. Sel. Topics Appl. Earth Observ. Remote Sens.*, vol. 14, pp. 12132–12148, 2021, doi: 10.1109/JSTARS.2021.3128938.
4. H. Yuan, H. Li, Y. Zhang, M. Li, C. Wei, “Few-shot classification for ISAR images of space targets by complex-valued patch graph transformer,” *IEEE Trans. Aerosp. Electron. Syst.*, vol. 60, no. 4, Aug. 2024, doi: 10.1109/TAES.2024.3382222.
5. X. Bai, M. Yang, B. Chen, F. Zhou, “REMI: Few-shot ISAR target classification via robust embedding and manifold inference,” *IEEE Trans. Neural Netw. Learn. Syst.*, vol. 36, no. 4, pp. 6000–6013, Apr. 2025, doi: 10.1109/TNNLS.2024.3391330.
6. M. Yang, B. Chen, Y. Wang, X. Bai, F. Zhou, “Few-shot multistatic ISAR target classification based on multilevel feature reconstruction,” *IEEE Trans. Geosci. Remote Sens.*, vol. 63, Art. no. 5106516, 2025, doi: 10.1109/TGRS.2025.3592206.
7. M.-D. Li, S.-P. Xiao, S.-W. Chen, “Compact polarimetric ISAR space target components recognition with dual-branch correlation aggregation graph attention network,” *IEEE Trans. Geosci. Remote Sens.*, vol. 63, Art. no. 5107917, 2025, doi: 10.1109/TGRS.2025.3607102.

**延伸阅读（经典教材与方法，非本文七篇）**：保铮等《雷达成像技术》；V. C. Chen & M. Martorella, *Inverse Synthetic Aperture Radar Imaging: Principles, Algorithms and Applications*；J.-S. Lee & E. Pottier, *Polarimetric Radar Imaging: From Basics to Applications*；J. Snell et al., “Prototypical Networks for Few-shot Learning” (NeurIPS 2017)；T. Chen et al., “A Simple Framework for Contrastive Learning of Visual Representations” (ICML 2020)；M. Jaderberg et al., “Spatial Transformer Networks” (NeurIPS 2015)。
