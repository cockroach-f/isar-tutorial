# 前言：这份文档怎么用

!!! warning "关于期刊原图"

    因版权限制，本站点**不转载** IEEE 等期刊论文中的原图。Part B 各章凡引用「原文 Fig. N」处，已改为斜体提示，请打开对应论文 PDF 对照。自绘简化框图与全部仿真图仍可在站内查看。



**读者画像。** 本文档面向电子信息工程专业二年级本科生：学过“信号与系统”（傅里叶变换、卷积、采样），会用 Python 或 MATLAB，但对雷达成像与深度学习了解不多。读完后你应当能够：

1. 说清楚 ISAR（逆合成孔径雷达）图像是怎么从雷达回波“算”出来的，以及它的分辨率由什么决定；
2. 理解极化、散焦、少样本、复值网络这些关键词在 ISAR 识别里为什么重要；
3. 独立读懂本文带读的 7 篇论文的方法、实验与结论，并知道它们彼此的关系；
4. 动手跑通两个入门项目：仿真 RD 像 + ResNet18 分类，以及原型网络少样本识别。

**结构。** 全文分三部分：

- **Part A 基础**（第 0–6 章）：数学与信号准备（第 0 章）、雷达与 ISAR 成像、极化、识别难点、深度学习入门（上、下两章）。每个概念都按“直觉类比 → 机理 → 可以手算的小例题 → 公式（逐个解释符号、不跳推导步骤）→ 配图”的顺序展开；配图均有 Python 代码（`code/`），关键处配有动画视频（`videos/`）。
- **Part B 逐篇带读**（第 7–13 章）：每篇论文按“背景与动机 → 要解决的问题 → 方法分步 → 数据与实验 → 结果 → 优缺点 → 本科生可复现内容 → 自测题”展开；同时给出自绘简化框图，并引用原文关键图（标注原文图号）。
- **Part C 综合**（第 14–16 章）：分类体系、横向对比表、研究趋势、阅读路线、入门项目、术语表；附录列出所有“存疑/未能核实”之处。

**七篇论文一览**（文中简称“论文 1–7”）：

| 编号 | 简称 | 题目（缩写） | 出处 | 单位 |
|---|---|---|---|---|
| 1 | DB-SSIT | Terahertz Polarimetric ISAR Target Recognition Based on a Dual-Branch Spatial-Scatter Interaction Transformer | Electromagnetic Science, 2025 | 上海理工大学 |
| 2 | CV-GNN | Complex-Valued Graph Neural Network on Space Target Classification for Defocused ISAR Images | IEEE GRSL, vol. 19, 2022 | 哈尔滨工业大学 |
| 3 | MSN | Meta-Learner-Based Stacking Network on Space Target Recognition for ISAR Images | IEEE JSTARS, vol. 14, 2021 | 哈尔滨工业大学 |
| 4 | CvPGT | Few-Shot Classification for ISAR Images of Space Targets by Complex-Valued Patch Graph Transformer | IEEE TAES, vol. 60, no. 4, 2024 | 哈尔滨工业大学 |
| 5 | REMI | REMI: Few-Shot ISAR Target Classification via Robust Embedding and Manifold Inference | IEEE TNNLS, vol. 36, no. 4, 2025 | 西安电子科技大学 |
| 6 | MLFR | Few-Shot Multistatic ISAR Target Classification Based on Multilevel Feature Reconstruction | IEEE TGRS, vol. 63, 2025 | 西安电子科技大学 |
| 7 | DCA-Net | Compact Polarimetric ISAR Space Target Components Recognition With Dual-Branch Correlation Aggregation Graph Attention Network | IEEE TGRS, vol. 63, 2025 | 国防科技大学 |

**第 2 版改了什么。** 第 1 版的基础部分写得太紧凑。第 2 版在保留原有结构、图、代码和已核实内容的基础上：

1. 新增第 0 章（复数、I/Q、傅里叶变换、采样、DFT、相关），把第 5 章拆成“深度学习入门（上）/（下）”两章；
2. 每个基础概念都补充了直觉类比、带具体数字的例题（共 30 余个，数值均用 Python 验算）、完整推导和新配图（`figures/v2_*.png`）；
3. 论文章节（第 7–13 章）开头增加“基础回链”框，方法的每一步都标出对应的基础小节，并配一句话的通俗解释；
4. 公式改用 MathJax 排版，统一编号，矩阵、多行推导与分段函数均经过逐页渲染检查。

**几种彩色框的含义。**

!!! tip "本章目标"

    每章开头：读完本章你应当掌握什么。

!!! info "直觉"

    用生活中的类比先建立直觉，再看公式。

!!! example "例题"

    带具体数字、可以用笔算的小例题。建议先自己算一遍，再看答案。

!!! success "关键公式"

    需要记住的关键公式，并附符号说明。

!!! warning "易错点"

    初学者最容易犯的错误。

!!! note "基础回链"

    论文章节需要用到的基础概念及其所在小节。

!!! abstract "小结"

    每章结尾的要点回顾。

> **关于准确性的约定。** 文中所有论文数据（参数、数据集规模、实验数值）均逐条对照论文原文（含表格截图）核对；凡是原文表述不清、可能有印刷错误或我无法核实的地方，用 **【存疑】** 标出，并在附录 B 汇总。仿真图均为教学用简化模型，数值不代表论文结果。“自绘”图为作者根据原文理解重新绘制的简化示意，原文图则注明“原文 Fig. x”。

> **视频。** HTML 版中可直接播放 4 段动画（每段 24–38 秒）；PDF 版中以关键帧代替并给出文件路径。
