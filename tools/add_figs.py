"""Insert additional original paper figures into Part B chapters, then renumber figures."""
import re
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "docs" / "part-b"

# (anchor substring, mode, figfile, width, caption, guide)
S = {
"B1_dbssit.md": [
 ("### 步骤 2：", "before", "p1_DBSSIT_fig2.png", "55%", "原文 Fig. 2：极化多尺度预处理模块。",
  "从上往下看：6 维极化特征先做多尺度卷积、BatchNorm 和池化，再经两个 1×1 卷积压缩通道，正好对应上面步骤 1 的文字。"),
 ("### 步骤 3：", "before", "p1_DBSSIT_fig4.png", "80%", "原文 Fig. 4：空间特征提取块 SFEB 的结构。",
  "上排是主干：3×3 卷积 → 3×3 深度卷积 → 3×3 卷积 → 空间注意力 SA；下方虚线框展开了 SA（MaxPool 与 AvgPool 拼接后卷积）。SFEB 与 PSFEB 并列，构成“双分支”中的空间分支。"),
 ("## 7.4 ", "before", "p1_DBSSIT_fig5.png", "70%", "原文 Fig. 5：局部–全局融合模块的结构。",
  "左列是主干，右侧两个灰框分别放大了带池化的多头自注意力（E-MHSA）和 LFFN（1×1 卷积 → 3×3 深度卷积 → 1×1 卷积）。看图时重点找“全局注意力”和“局部卷积”是怎样交替出现的。"),
 ("## 7.5 ", "before", "p1_DBSSIT_fig7.png", "80%", "原文 Fig. 7：不同类型的合成图像。",
  "这是送入网络前的合成图像示例，可与上面 Fig. 6 的单极化图对照。具体合成方式以原文正文为准。"),
 ("**可视化**：", "after", "p1_DBSSIT_fig9.png", "100%", "原文 Fig. 9：不同模型在同一测试集上的特征降维（t-SNE）可视化。",
  "每个点是一个测试样本，颜色代表类别。簇越紧凑、不同颜色分得越开，说明特征越容易区分。t-SNE 只能定性比较，布局本身没有物理意义。"),
 ("**可视化**：", "after2", "p1_DBSSIT_fig10.png", "100%", "原文 Fig. 10：不同模型在同一测试集上的混淆矩阵。",
  "行是真实类别、列是预测类别：对角线越深越好，非对角格子说明哪两类容易混淆。可以比较最后一幅 DB-SSIT 与其他模型的非对角元素。"),
],
"B2_cvgnn.md": [
 ("## 8.3 ", "before", "p2_CVGNN_fig1.png", "85%", "原文 Fig. 1：机动与慢速空间目标的天基 ISAR 成像几何及成像结果。",
  "上半部分是雷达与目标的轨道几何，下半部分左为聚焦像、右为机动目标的散焦像。注意散焦像沿横向的拖尾，这正是 CV-GNN 想“不重聚焦直接识别”的输入。"),
 ("### 步骤 4：", "before", "p2_CVGNN_fig3.png", "85%", "原文 Fig. 3：邻接层示意图。",
  "两两节点的特征先求差的绝对值，再经过多层复值卷积 + 复值 BN + ReLU，最后 softmax，得到可学习的边权。"),
 ("### 步骤 4：", "before", "p2_CVGNN_fig4.png", "85%", "原文 Fig. 4：图卷积层示意图。",
  "节点由“样本表示 ⊕ 复值标签”构成；图卷积用邻接层给出的边权聚合邻居，再经复值线性层更新节点。上下两部分分别对应正文的邻接层和图卷积层。"),
 ("## 8.4 ", "before", "p2_CVGNN_fig6.png", "85%", "原文 Fig. 6：CV-GNN 的整体结构（逐层配置）。",
  "左栏是复值特征提取网络的逐层参数，右栏是邻接层与图卷积模块的堆叠方式，可以和步骤 1–3 一一对照。"),
 ("**消融 1（原文 Fig. 7", "after", "p2_CVGNN_fig7.png", "70%", "原文 Fig. 7：CV-GNN 与 RV-GNN 的损失曲线。",
  "四条曲线分别是两种网络在聚焦和散焦数据上的训练损失。重点比较散焦数据上 RV-GNN 与 CV-GNN 的收敛位置，对应正文的消融 1。"),
 ("**消融 2（原文 Fig. 8", "after", "p2_CVGNN_fig8.png", "90%", "原文 Fig. 8：总体精度与 Kappa 系数曲线。(a) 随类别数变化；(b) 随训练样本数变化。",
  "横轴分别是类别数和每类训练样本数，纵轴是 OA 或 Kappa。看 CV-GNN 曲线与 CV-CNN 等对比方法之间的差距怎样随横轴变化。"),
],
"B3_msn.md": [
 ("## 9.3 ", "before", "p3_MSN_fig3.png", "90%", "原文 Fig. 3：ISAR 图像识别的总体难点。",
  "左侧列出 ISAR 成像特点与分类要求，右侧把“难点”和“对应对策”配成对。可以把它当作 MSN 设计动机的总览。"),
 ("### 步骤 2：", "before", "p3_MSN_fig4.png", "100%", "原文 Fig. 4：ISAR 图像预处理示例。(a) 原始数据；(b) 增强 Lee 滤波；(c) 幂变换；(d) 能量归一化。",
  "从 (a) 到 (d) 依次看：滤波压低斑点噪声，幂变换让弱散射点更明显，能量归一化统一亮度尺度。"),
 ("### 步骤 3：", "before", "p3_MSN_fig5.png", "85%", "原文 Fig. 5：旋转注意力模块 RAM 的结构。",
  "左侧把特征图旋转出多个角度，中间分别做空间注意力，右侧取平均融合。目的是让注意力对目标姿态（旋转）更稳健。"),
 ("### 步骤 3：", "before", "p3_MSN_fig6.png", "60%", "原文 Fig. 6：旋转操作示意。",
  "演示像素坐标旋转后怎样映射回网格：旋转后的位置通常落在格点之间，需要用邻近像素插值。"),
 ("### 步骤 3：", "before", "p3_MSN_fig7.png", "90%", "原文 Fig. 7：把 RAM 模块加入 ResNet50 后的网络结构。",
  "上排是 ResNet50 的四个 stage，下方放大了插入 RAM 的瓶颈块，可以看出 RAM 放在哪一层。"),
 ("### 步骤 4：", "before", "p3_MSN_fig8.png", "90%", "原文 Fig. 8：图卷积网络（GCN）结构。",
  "流程是先提取特征，再把样本当节点、用学习到的相似度构图，最后做图卷积分类。与第 6.2 节的少样本 GNN 思路一致。"),
 ("### 步骤 5：", "before", "p3_MSN_fig9.png", "75%", "原文 Fig. 9：关系网络（RN）结构。",
  "嵌入模块 f 提取特征，把查询样本与每个支持样本的特征拼接后送入关系模块 g，输出关系分数，分数最高的就是预测类别。"),
 ("- 原文 Fig. 13 的 Grad-CAM", "before", "p3_MSN_fig12.png", "100%", "原文 Fig. 12：损失与精度曲线。(a) ResNet50；(b) ResNet50 + RAM；(c) RN；(d) GCN。",
  "四个基学习器各自的训练/验证曲线。重点看是否收敛、训练与验证之间有没有明显差距（过拟合）。"),
 ("- 实测 Tiangong-1", "before", "p3_MSN_fig13.png", "100%", "原文 Fig. 13：Grad-CAM 注意力热力图。(a) 卫星 1–5 的原始 ISAR 像；(b) 加入 RAM 后的热力图。",
  "热区越集中在目标散射区域越好。对照正文：加入 RAM 后注意力更集中在目标上。"),
 ("- 实测 Tiangong-1", "before", "p3_MSN_fig14.png", "100%", "原文 Fig. 14：特征重要性分布。(a) 自适应加权 XGBoost；(b) 普通 XGBoost。",
  "纵轴是三个基学习器输出的各维特征，横轴是 XGBoost 给出的重要性。比较两幅图里重要性分布的差异，理解“自适应加权”改变了什么。"),
 ("- 实测 Tiangong-1", "after", "p3_MSN_fig15.png", "75%", "原文 Fig. 15：不同姿态下的实测 ISAR 像。",
  "这是实测验证用的天宫一号图像示例，与上面 Fig. 11 的仿真像对比，实测图像更不规则、背景更复杂。"),
 ("- 实测 Tiangong-1", "after2", "p3_MSN_fig16.png", "60%", "原文 Fig. 16：不同方法的分类置信度。",
  "柱高是各方法对实测样本的分类置信度。各方法都在 0.9 以上，差距不大，解读时不要过度放大。"),
],
"B4_cvpgt.md": [
 ("原文 Fig. 1 对比了经典分类", "after", "p4_CvPGT_fig1.png", "70%", "原文 Fig. 1：经典分类与少样本分类的区别。",
  "上方是经典分类：训练与测试类别相同。下方是少样本：数据组织成一个个任务，每个任务有支持集和查询集，测试类别是训练中没见过的新类。"),
 ("### 模块 2：", "before", "p4_CvPGT_fig3.png", "100%", "原文 Fig. 3：对比学习流程。",
  "同一张复值图像经过不同的随机成像参数变换，得到两个“视角”，通过编码器后拉近彼此、推远其他样本，使特征对分辨率、散焦、旋转不敏感。"),
 ("### 模块 3：", "before", "p4_CvPGT_fig4.png", "85%", "原文 Fig. 4：雷达与机动目标的轨道，以及基于图像块的节点表示方式。",
  "下半部分演示把 ISAR 像切成重叠的 patch，每个 patch 是一个图节点。这是 PGT 模块的输入构造方式。"),
 ("### 模块 3：", "before", "p4_CvPGT_fig5.png", "100%", "原文 Fig. 5：PGT 特征提取模块的完整流程。",
  "从左到右：切 patch → 复值图推理（局部关系）→ 复值 Transformer（全局关系）→ 输出 patch 级特征，与整图特征合并。"),
 ("### 模块 3：", "before", "p4_CvPGT_fig6.png", "70%", "原文 Fig. 6：全局聚合过程流程图。",
  "对应正文第 4 步的复值 Transformer：复数 q、k、v 做自注意力，再经复值 LayerNorm 和 MLP，两处 add 是残差连接。"),
 ("### 模块 3：", "before", "p4_CvPGT_fig7.png", "55%", "原文 Fig. 7：嵌入网络的详细结构。",
  "整幅复值图像依次经过 CV-Conv、CV-BN2D、CV-ReLU 和 CV-Maxpool，特征尺寸从 32×32 逐步降到 1×1，得到全局特征 E_w。"),
 ("## 10.5 ", "before", "p4_CvPGT_fig8.png", "85%", "原文 Fig. 8：八类空间目标的光学图像与 ISAR 像。",
  "每类上方为光学图像（模型外观），下方为对应的仿真 ISAR 像，可以感受“光学上差异大，ISAR 上却只剩稀疏散射点”。"),
 ("## 10.5 ", "before", "p4_CvPGT_fig11.png", "75%", "原文 Fig. 11：三个实验室实测目标 SZ-13、CE-2、TG-2 的光学与雷达图像。",
  "上方是暗室中的缩比模型，下方是实测雷达像。它们构成正文中的实验室实测数据。"),
 ("**数据量与分辨率的影响（原文 Fig. 9）**", "after", "p4_CvPGT_fig9.png", "100%", "原文 Fig. 9：3-way 5-shot 与 3-way 1-shot 场景下的分类率及其二次函数拟合曲线。",
  "横轴是横滚角步长或图像分辨率，纵轴是分类率，曲线是二次拟合。看精度随数据量减少、分辨率降低怎样下降。"),
 ("**表 10-2 与其他方法对比", "before", "p4_CvPGT_fig10.png", "100%", "原文 Fig. 10：不同转速、转动加速度数据集在 1-shot 与 5-shot 任务中的测试精度直方图与平均精度。",
  "每个直方图是 100 次重复测试的精度分布，对应表 10-1。5-shot 的分布明显更窄、更靠右，说明更稳定。"),
 ("**实验室实测（原文 Table VI、VII）**", "after", "p4_CvPGT_fig12.png", "70%", "原文 Fig. 12：实测数据集在 1-shot 与 5-shot 任务中的测试精度直方图与平均精度。(a) 1-shot；(b) 5-shot。",
  "上方小表给出最小、最大、均值和标准差，下方是分布。实测均值（70.07% / 76.27%）低于仿真，说明仿真到实测存在差距。"),
 ("## 10.6 ", "before", "p4_CvPGT_fig14.png", "70%", "原文 Fig. 14：不同网络框架的训练损失。",
  "比较复值 CvPGT 与同层数实值 RvPGT 的训练损失曲线，看复值版本是否收敛更低、更快。"),
 ("## 10.6 ", "before", "p4_CvPGT_fig15.png", "70%", "原文 Fig. 15：不同模型在 (a) 3-way 1-shot 和 (b) 3-way 5-shot 场景、不同数据集上的分类精度直方图。",
  "每组柱子是一个测试数据集，颜色区分方法，可以与表 10-2 的数字互相印证。"),
],
"B5_remi.md": [
 ("**(2) GEN", "before", "p5_REMI_fig3.png", "90%", "原文 Fig. 3：MH-STN 的详细结构。",
  "输入 ISAR 像经若干卷积 + 池化层回归出多组变换参数（多头），每个头给出一种无剪切的仿射校正。“多头”是为了在不同假设下校正形变，减少单个 STN 的错误校正。"),
 ("### 阶段 2：", "before", "p5_REMI_fig4.png", "95%", "原文 Fig. 4：GEN 的详细结构。",
  "上排是整体流程；下方左框是分组卷积，右框是特征融合模块。分组卷积让不同组分别处理多头校正后的图像，参数和计算量反而下降（见表 11-2 的 FLOPs）。"),
 ("## 11.4 ", "before", "p5_REMI_fig5.png", "100%", "原文 Fig. 5：MG-GAT 示意图。",
  "左侧是节点注意力更新，右侧是节点特征更新，下方小图展示邻接矩阵与特征分布在迭代中的变化。要点是在流形上传播，避免普通 GAT 的过平滑。"),
 ("| 目标 | 7 颗卫星", "after", "p5_REMI_fig6.png", "100%", "原文 Fig. 6：各卫星的光学图像与典型 ISAR 像。",
  "上排是七颗卫星的光学外观，下排是对应 ISAR 像，可以感受不同卫星在 ISAR 像中的差别有多细微。"),
 ("**表 11-2 消融实验", "before", "p5_REMI_fig8.png", "100%", "原文 Fig. 8：各场景 3-way 1-shot / 5-shot 的混淆矩阵。",
  "截图上方附带了原文的对比表（数字已整理进表 11-1），下方是各场景、各设置的混淆矩阵，看哪几类卫星最容易混淆。"),
 ("**表 11-2 消融实验", "before", "p5_REMI_fig9.png", "100%", "原文 Fig. 9：(a)–(d) 场景 I–IV 的分类精度直方图。",
  "每个直方图是大量测试任务的精度分布，与对比方法的分布叠在一起。REMI 的分布整体右移，说明不是靠个别好运气的任务。"),
 ("**实测飞机数据", "after", "p5_REMI_fig10.png", "85%", "原文 Fig. 10：飞机的光学图像与典型 ISAR 像。",
  "这是“仿真基类 → 实测新类”实验所用的飞机示例。上排为光学图像，下排为 ISAR 像。"),
 ("## 11.6 ", "before", "p5_REMI_fig12.png", "85%", "原文 Fig. 12：MG-GAT 与 GAT 的注意力动态可视化。",
  "每列是一层的注意力（邻接）矩阵，最右为真实类别关系。看 MG-GAT 的矩阵是否随层数逐渐接近块状的 ground truth，而 GAT 是否变得模糊（过平滑）。"),
],
"B6_mlfr.md": [
 ("![图 12-1 原文 Fig. 6", "before", "p6_MLFR_fig1.png", "80%", "原文 Fig. 1：限制多站 ISAR 目标分类性能的主要因素。",
  "左侧：同一目标在不同站的图像差异很大（类内差异大）；右侧：不同目标的图像可能很像（类间区分不足）。这两点分别对应后面的 ISFR 与 ICFR。"),
 ("### 步骤 3：", "before", "p6_MLFR_fig3.png", "80%", "原文 Fig. 3：ISFR 的详细流程。",
  "左半是特征对齐：把各站的中间特征图做空间变换，对齐到统一姿态；右半是站间重建：用多头注意力等结构融合各站信息。注意先对齐、后重建的顺序（消融里 ISFR‡ 正说明了顺序的重要性）。"),
 ("| 站数 | 3 个站", "after", "p6_MLFR_fig5.png", "70%", "原文 Fig. 5：同一时段内不同站对目标的连续共视观测。",
  "三个站从不同位置同时观测同一目标的轨迹段，这是“多站”数据的来源。"),
 ("**表 12-3 参数量与计算量", "before", "p6_MLFR_fig7.png", "100%", "原文 Fig. 7：1000 次独立实验的精度分布直方图。(a) 3-way 1-shot；(b) 3-way 5-shot；(c) 二者合并。",
  "分布越窄、越靠右越好。它对应表 12-2 中均值 ± 置信区间背后的完整分布。"),
 ("![图 12-5 原文 Fig. 9", "before", "p6_MLFR_fig8.png", "85%", "原文 Fig. 8：应用 ISFR + ICFR 前（左）后（右）三个类别的特征可视化。",
  "左图三类点混在一起，右图分成三簇，直观展示两个重建模块的作用（同样只是定性展示）。"),
],
"B7_dcanet.md": [
 ("![图 13-1 原文 Fig. 3", "before", "p7_DCANet_fig1.png", "75%", "原文 Fig. 1：本文动机。(a) 用于构图的局部与全局部件关系拓扑；(b) 图特征的相干叠加。",
  "(a) 展示同一部件的多个冗余框（局部关系）和同类部件之间（全局关系）怎样连成图；(b) 说明通过图聚合，同类部件的特征可以相干增强。"),
 ("![图 13-1 原文 Fig. 3", "before", "p7_DCANet_fig2.png", "70%", "原文 Fig. 2：基于 CNN 与基于 GNN 的识别流程对比。",
  "(a) 是常规 CNN 检测流程；(b)(c) 在检测头后加入图推理与信息反馈。DCA-Net 属于 (c) 的无锚框反馈方式。"),
 ("**(3) DCAG", "before", "p7_DCANet_fig5.png", "85%", "原文 Fig. 5：MGNF 模块流程图。",
  "从左到右：提取锚点特征 → 估计多高斯分布 → 过滤背景节点 → 得到稀疏的目标节点，用于后续构图。"),
 ("### 损失", "before", "p7_DCANet_fig6.png", "90%", "原文 Fig. 6：DCAG 模块的详细结构。",
  "上半是全局图构建，下半是局部图构建，两路图特征最后融合。对应正文的“双分支相关聚合”。"),
 ("## 13.5 ", "before", "p7_DCANet_fig7.png", "45%", "原文 Fig. 7：六颗卫星的精细 CAD 模型（左）与伪彩色 ISAR 像（右）。",
  "CAD 图中不同颜色代表不同部件类别；右侧是对应的简缩极化伪彩色 ISAR 像，可以对照看每类部件在 ISAR 像里大致是什么样。"),
 ("## 13.5 ", "before", "p7_DCANet_fig8.png", "80%", "原文 Fig. 8：ISAR 空间目标部件标注方法示意。",
  "左上表列出部件类型（本体、太阳翼、天线、附件、光学镜头等），下方演示在三维模型上标注后投影到成像平面得到旋转框。"),
 ("## 13.5 ", "before", "p7_DCANet_fig9.png", "50%", "原文 Fig. 9：六颗卫星的 (a) 部件数量、(b) 部件面积、(c) 部件长宽比、(d) 部件朝向角直方图。",
  "这张图说明部件尺度、长宽比差异很大，对应背景中的“困难”一条。"),
 ("![图 13-4 原文 Fig. 10", "after", "p7_DCANet_fig11.png", "50%", "原文 Fig. 11：40°、45°、50° 三个俯仰角下的归一化混淆矩阵对比：(a) O-RTMdet；(b) O-RRCNN；(c) DCA-Net。",
  "对角线是各部件类别的召回率，重点看板状附件、杆状附件两行，对应正文“其他分析”里的召回率提升。"),
 ("![图 13-4 原文 Fig. 10", "after2", "p7_DCANet_fig12.png", "70%", "原文 Fig. 12：(a) 局部最优 OBB 数量与 (b) 每个最优 OBB 平均对应的冗余 OBB 数量直方图。",
  "说明每个部件周围常有多个冗余候选框，这是局部构图的依据。"),
 ("![图 13-4 原文 Fig. 10", "after3", "p7_DCANet_fig13.png", "70%", "原文 Fig. 13：不加 (c) 与加入 (d) DCAG 模块时多层深度特征的热力图；(a)(b) 为伪彩色 ISAR 像与部件标注。",
  "比较 (c)(d)：加入 DCAG 后，热区是否更贴合标注的部件位置，尤其是弱散射部件。"),
 ("![图 13-4 原文 Fig. 10", "after4", "p7_DCANet_fig14.png", "70%", "原文 Fig. 14：局部构图中目标节点与周围源节点的 OBB 可视化。(a)(b) 为板状附件；(c)(d) 为太阳翼。",
  "图中显示局部图里哪些候选框被连到同一个目标节点上，帮助理解“同一部件的冗余框互相支撑”。"),
 ("![图 13-4 原文 Fig. 10", "after5", "p7_DCANet_fig15.png", "75%", "原文 Fig. 15：局部图的 Spearman 相关系数。",
  "衡量局部图中节点特征之间的相关程度，可与 Fig. 17 的全局图对照。"),
 ("![图 13-4 原文 Fig. 10", "after6", "p7_DCANet_fig16.png", "70%", "原文 Fig. 16：全局构图中目标节点与周围源节点的 OBB 可视化。(a)(b) 分别为板状附件和太阳翼的情况。",
  "与 Fig. 14 对照：全局图把同类但不相邻的部件也连了起来。"),
 ("![图 13-4 原文 Fig. 10", "after7", "p7_DCANet_fig17.png", "75%", "原文 Fig. 17：全局图的 Spearman 相关系数。",
  "与 Fig. 15 对照，比较局部图与全局图的相关性特点；具体结论以原文讨论为准。"),
],
}

def block(fig, width, cap, guide):
    return [f'![{cap}](../paper_figs/{fig}){{ width="{width}" loading=lazy }}', "", f"> **读图：** {guide}", ""]

def find_para_end(lines, i):
    j = i
    while j < len(lines) and lines[j].strip() != "":
        j += 1
    return j  # index of blank line

for name, specs in S.items():
    p = D / name
    lines = p.read_text(encoding="utf-8").split("\n")
    for anchor, mode, fig, w, cap, guide in specs:
        if f"paper_figs/{fig}" in "\n".join(lines):
            continue
        idx = next((k for k, l in enumerate(lines) if anchor in l), None)
        if idx is None:
            raise SystemExit(f"{name}: anchor not found: {anchor}")
        b = block(fig, w, cap, guide)
        if mode == "before":
            lines[idx:idx] = b
        else:
            # after the paragraph containing anchor; afterN = skip N-1 following figure blocks
            n = int(mode[5:] or 1)
            j = find_para_end(lines, idx)
            for _ in range(n - 1):
                # skip blank lines, then next block (image + blank + guide + blank)
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                j = find_para_end(lines, j)  # image line
                while j < len(lines) and lines[j].strip() == "":
                    j += 1
                if j < len(lines) and lines[j].startswith("> **读图"):
                    j = find_para_end(lines, j)
            lines[j + 1:j + 1] = b
    text = "\n".join(lines)
    # renumber 图 N-M in image alts for this chapter
    ch = re.search(r"^# 第 (\d+) 章", text, re.M).group(1)
    k = 0
    def rn(m):
        global k
        k += 1
        return f"![图 {ch}-{k} "
    k = 0
    def rn2(m, c=[0]):
        c[0] += 1
        return f"![图 {ch}-{c[0]} "
    # strip existing numbers and add new uniformly to all images
    text = re.sub(r"!\[(?:图 \d+-\d+[a-z]? )?", lambda m, c=[0]: (c.__setitem__(0, c[0] + 1) or f"![图 {ch}-{c[0]} "), text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    p.write_text(text, encoding="utf-8")
    print(name, "images:", len(re.findall(r"!\[", text)), "paper_figs:", len(re.findall(r"paper_figs/", text)))
