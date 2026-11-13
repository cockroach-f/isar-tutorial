# 前言：这份文档怎么用

**先修知识。** 建议具备信号与系统基础（傅里叶变换、卷积、采样），会用 Python 或 MATLAB。读完后你应当能够：

1. 说清楚 ISAR（逆合成孔径雷达）图像是怎么从雷达回波“算”出来的，以及它的分辨率由什么决定；
2. 理解极化、散焦、少样本、复值网络这些关键词在 ISAR 识别里为什么重要；
3. 独立读懂本文带读的 7 篇论文的方法、实验与结论，并知道它们彼此的关系；
4. 动手跑通两个入门项目：仿真 RD 像 + ResNet18 分类，以及原型网络少样本识别。

**结构。** 全文分三部分：

- **Part A 基础**（第 0–6 章）：数学与信号准备（第 0 章）、雷达与 ISAR 成像、极化、识别难点、深度学习入门（上、下两章）。每个概念都按“直觉类比 → 机理 → 可以手算的小例题 → 公式（逐个解释符号、不跳推导步骤）→ 配图”的顺序展开；配图均有 Python 代码（`code/`），关键处配有动画视频（`videos/`）。
- **Part B 逐篇带读**（第 7–13 章）：每篇论文按“背景与动机 → 要解决的问题 → 方法分步 → 数据与实验 → 结果 → 优缺点 → 可动手复现的内容 → 自测题”展开；同时给出自绘简化框图，并引用原文关键图（标注原文图号）。
- **Part C 综合**（第 14–16 章）：分类体系、横向对比表、研究趋势、阅读路线、入门项目、术语表；附录列出所有“存疑/未能核实”之处。

**七篇论文一览**（文中用方法简称指代）：

| 方法 | 中文说明 | 题目（缩写） | 出处 | 单位 |
|---|---|---|---|---|
| DB-SSIT | 双分支空间-散射交互 Transformer | Terahertz Polarimetric ISAR Target Recognition Based on a Dual-Branch Spatial-Scatter Interaction Transformer | Electromagnetic Science, 2025 | 上海理工大学 |
| CV-GNN | 复值图神经网络 | Complex-Valued Graph Neural Network on Space Target Classification for Defocused ISAR Images | IEEE GRSL, vol. 19, 2022 | 哈尔滨工业大学 |
| MSN | 元学习器堆叠集成网络 | Meta-Learner-Based Stacking Network on Space Target Recognition for ISAR Images | IEEE JSTARS, vol. 14, 2021 | 哈尔滨工业大学 |
| CvPGT | 复值 Patch 图 Transformer | Few-Shot Classification for ISAR Images of Space Targets by Complex-Valued Patch Graph Transformer | IEEE TAES, vol. 60, no. 4, 2024 | 哈尔滨工业大学 |
| REMI | 鲁棒嵌入与流形推理 | REMI: Few-Shot ISAR Target Classification via Robust Embedding and Manifold Inference | IEEE TNNLS, vol. 36, no. 4, 2025 | 西安电子科技大学 |
| MLFR | 多层级特征重建 | Few-Shot Multistatic ISAR Target Classification Based on Multilevel Feature Reconstruction | IEEE TGRS, vol. 63, 2025 | 西安电子科技大学 |
| DCA-Net | 双分支相关聚合图注意力网络 | Compact Polarimetric ISAR Space Target Components Recognition With Dual-Branch Correlation Aggregation Graph Attention Network | IEEE TGRS, vol. 63, 2025 | 国防科技大学 |

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

> **视频。** 第 1、2、3、6、7、12 章正文的相关小节里嵌有 14 段动画（每段约 24–41 秒），可直接播放。
