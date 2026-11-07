# ISAR 目标识别入门与文献带读

面向初学者的 ISAR（逆合成孔径雷达）目标识别系统教学文档，含基础篇、七篇前沿文献带读、入门项目与术语表。

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

## 部署

当前站点由 `gh-pages` 分支托管（本地 `mkdocs build` 后推送）。

若你的 GitHub token 具备 `workflow` 权限，可把仓库里的
`.github/workflows/pages.yml`（见本仓库历史或重新添加）推上去，
改为 Actions 自动构建，并把 Pages 源切到 “GitHub Actions”。
