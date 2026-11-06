# ISAR 目标识别入门与文献带读

面向电子信息工程本科生的 ISAR（逆合成孔径雷达）目标识别系统教学文档，含基础篇、七篇前沿文献带读、入门项目与术语表。

**在线阅读：** <https://cockroach-f.github.io/isar-tutorial/>

## 本地预览

```bash
pip install mkdocs-material
mkdocs serve
```

浏览器打开提示的本地地址（默认 `http://127.0.0.1:8000`）。

## 目录结构

```
docs/
  index.md              # 前言
  part-a/ … part-c/     # 正文章节
  appendix.md            # 附录
  figures/              # 自绘与仿真图
  videos/               # 4 段教学动画
  code/                 # 可运行仿真与入门项目代码
```

> **版权说明：** 期刊论文原图（`paper_figs/`）未纳入本仓库。正文对应位置改为「请对照原文 Fig. N」的提示；请自行打开 PDF 对照。

## 部署

推送到 `main` 后，GitHub Actions 会自动构建并发布到 GitHub Pages。
