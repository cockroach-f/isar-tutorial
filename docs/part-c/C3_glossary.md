# 第 16 章 术语表

| 术语 | 英文 | 解释 | 首次出现 |
|---|---|---|---|
| 复数 / 相量 | Complex Number / Phasor | $z=Ae^{j\varphi}$，可看作平面上的箭头；乘 $e^{j\theta}$ = 旋转 | 0.1 |
| 相位 | Phase | 箭头的角度；雷达中 $\Delta\varphi = 4\pi\Delta R/\lambda$ | 0.1 |
| I/Q | In-phase / Quadrature | 正交解调输出的两路信号，$I+jQ = Ae^{j\varphi}$ | 0.2 |
| 傅里叶变换 / 频谱 | Fourier Transform / Spectrum | 把信号分解为不同频率的复指数 | 0.3 |
| 采样 / 混叠 | Sampling / Aliasing | 采样率不足时高频被误认成低频 | 0.4 |
| DFT / FFT | Discrete / Fast Fourier Transform | 离散傅里叶变换及其快速算法 | 0.5 |
| 相关 / 卷积 | Correlation / Convolution | 模板滑动“对应相乘再相加”；匹配滤波与 CNN 的共同核心 | 0.6 |
| ISAR | Inverse Synthetic Aperture Radar | 逆合成孔径雷达，利用目标转动获得横向分辨率的成像雷达 | 第 2 章 |
| SAR | Synthetic Aperture Radar | 合成孔径雷达，利用雷达平台运动成像 | 第 2 章 |
| LFM / chirp | Linear Frequency Modulation | 线性调频信号，瞬时频率随时间线性变化 | 1.3 |
| 匹配滤波 | Matched Filter | 冲激响应为发射信号共轭翻转的滤波器，输出信噪比最大 | 1.4 |
| 脉冲压缩 | Pulse Compression | 用匹配滤波把长宽带脉冲压缩为窄峰 | 1.4 |
| 时宽带宽积 | Time-Bandwidth Product | $T_pB$，压缩比 | 1.4 |
| HRRP | High Resolution Range Profile | 一维高分辨距离像 | 1.5 |
| 快时间 / 慢时间 | Fast / Slow Time | 脉冲内的时间（对应距离）/ 脉冲间的时间（对应多普勒） | 2.2 |
| 转台模型 | Turntable Model | 平动补偿后，目标等效为绕中心旋转 | 2.2 |
| 多普勒 | Doppler | 由径向速度引起的频移，ISAR 中正比于横向坐标 | 2.2 |
| RD 算法 | Range-Doppler Algorithm | 距离压缩 + 方位 FFT 的 ISAR 成像算法 | 2.3 |
| BP / PFA | Back Projection / Polar Format Algorithm | 后向投影 / 极坐标格式成像算法（论文 5 / 论文 7 使用） | 2.7 |
| 积累角 | Accumulation Angle $\Delta\theta$ | 成像期间目标相对雷达转过的总角度 | 2.4 |
| 散焦 | Defocus | 非匀速转动等导致的图像模糊 | 2.5 |
| MTRC | Migration Through Resolution Cells | 越分辨单元走动 | 2.5 |
| 运动补偿 | Motion Compensation | 包络对齐 + 相位校正 | 2.6 |
| 自聚焦 | Autofocus（PGA、最小熵） | 估计并补偿相位误差 | 2.6 |
| 散射中心 | Scattering Center | 高频区目标散射的等效点源 | 2.7 |
| FEKO / PO | — / Physical Optics | 电磁仿真软件 / 物理光学近似方法 | 2.7 |
| 极化 | Polarization | 电场振动方向；H、V、L、R | 3.1 |
| 散射矩阵 | Sinclair Matrix $\mathbf S$ | 2×2 复矩阵，描述目标对极化的变换 | 3.2 |
| 互易性 | Reciprocity | 单站下 $S_{HV}=S_{VH}$ | 3.2 |
| Pauli 分解 | Pauli Decomposition | 奇次 / 偶次 / 交叉三分量 | 3.3 |
| 相干矩阵 | Coherency Matrix $\mathbf T$ | $\langle\mathbf k\mathbf k^H\rangle$ | 3.4 |
| Span | Span | 总功率 $T_{11}+T_{22}+T_{33}$ | 3.4 |
| 简缩极化 | Compact Polarimetry（DCP） | 单发双收的极化模式 | 3.5 |
| 伪彩色 | Pseudo-color | 用 RGB 三通道表示三种散射分量 | 3.3 |
| 神经元 / MLP | Neuron / Multi-Layer Perceptron | 加权和 + 偏置 + 非线性；多层堆叠为全连接网络 | 5.1 |
| 激活函数 | Activation Function | ReLU、sigmoid、tanh、Mish 等非线性函数 | 5.1 |
| softmax | Softmax | 把分数变成和为 1 的概率 | 5.1 |
| 交叉熵 | Cross-Entropy | 分类损失 $-\log p_y$，梯度为 $\mathbf p-\mathbf y$ | 5.2 |
| 反向传播 / 梯度下降 | Backpropagation / Gradient Descent | 用链式法则求梯度，沿负梯度更新参数 | 5.2 |
| 过拟合 | Overfitting | 训练集好、测试集差 | 5.2 |
| 卷积层 / 池化 | Convolution / Pooling | 滑动模板提取局部特征 / 下采样 | 5.3 |
| CNN | Convolutional Neural Network | 卷积神经网络 | 5.4 |
| BN | Batch Normalization | 批归一化 | 5.4 |
| ResNet | Residual Network | 残差网络 | 5.4 |
| 分组卷积 / 深度卷积 | Group / Depthwise Conv | 通道分组独立卷积 | 5.4 |
| 注意力 | Attention | 学习权重对特征加权 | 6.1 |
| Transformer / ViT | — / Vision Transformer | 基于自注意力的网络 / 用于图像的 Transformer | 6.1 |
| GNN / GAT | Graph Neural Network / Graph Attention Network | 图神经网络 / 图注意力网络 | 6.2 |
| 少样本学习 | Few-Shot Learning | 每类极少标注样本下的识别 | 6.3 |
| N-way K-shot | — | 任务含 N 类，每类 K 个支持样本 | 6.3 |
| 支持集 / 查询集 | Support / Query Set | 带标签的参考样本 / 待分类样本 | 6.3 |
| 基类 / 新类 | Base / Novel Classes | 训练用类别 / 测试用的新类别，二者不相交 | 6.3 |
| Episode | Episode | 一个少样本任务 | 6.3 |
| 原型网络 | Prototypical Network | 以类中心为原型的度量学习方法 | 6.3 |
| 关系网络 | Relation Network | 学习样本间关系分数 | 6.3 |
| MAML | Model-Agnostic Meta-Learning | 学习易于快速适应的初始化 | 6.3 |
| 复值网络 | Complex-Valued Neural Network | 权重与运算均为复数的网络 | 6.5 |
| 对比学习 | Contrastive Learning | 拉近正样本、推远负样本的表征学习 | 6.4 |
| NT-Xent / InfoNCE | — | 对比学习常用损失 | 6.4 |
| STN | Spatial Transformer Network | 可微的仿射校正模块 | 6.6 |
| Stacking | Stacking | 两层集成学习：基学习器 + 元学习器 | 9.2 |
| XGBoost | eXtreme Gradient Boosting | 梯度提升树 | 9.3 |
| 多站 ISAR | Multistatic ISAR | 多部雷达协同观测 | 12.2 |
| 早期 / 中期 / 晚期融合 | Early / Mid / Late Fusion | 在输入 / 特征 / 决策层融合 | 12.2 |
| SSIM | Structural Similarity | 结构相似度 | 12.3 |
| OBB | Oriented Bounding Box | 旋转框 | 13.2 |
| NMS | Non-Maximum Suppression | 非极大值抑制，去除冗余框 | 13.3 |
| IoU | Intersection over Union | 交并比 | 13.3 |
| mAP50 | mean Average Precision @ IoU 0.5 | 检测平均精度 | 13.5 |
| OA / AA / Kappa | — | 总体精度 / 平均精度 / Kappa 系数 | 6.7 |
| Grad-CAM / t-SNE | — | 类激活热力图 / 高维特征降维可视化 | 6.7 |
| FLOPs / Params | — | 浮点运算量 / 参数量 | 6.7 |
