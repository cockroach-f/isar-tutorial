#!/usr/bin/env bash
# 渲染 docs/code/manim/*_scenes.py 中的 manim 场景 → docs/videos/<Scene>.mp4（720p30，H.264 CRF 30）
# 并截取封面 docs/figures/video_frames/<Scene>.jpg（用作 <video poster>）。
# 用法：tools/render_manim.sh [scene_file.py] [Scene ...]   （不带参数则渲染全部以 M 开头的场景）
# 依赖：Manim Community ≥0.18、ffmpeg、TeX（latex + dvisvgm），中文字体 Noto Sans CJK SC。
set -euo pipefail
TINYTEX_BIN="${TINYTEX_BIN:-/workspace/tools/.TinyTeX/bin/x86_64-linux}"
[[ -d "$TINYTEX_BIN" ]] && export PATH="$TINYTEX_BIN:$PATH"
MANIM="${MANIM:-manim}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/docs/code/manim"
export PYTHONDONTWRITEBYTECODE=1
MEDIA="${MEDIA_DIR:-/tmp/isar_manim_media}"
OUT="$ROOT/docs/videos"; POS="$ROOT/docs/figures/video_frames"
mkdir -p "$OUT" "$POS"
files=("${1:-}")
if [[ -z "${files[0]}" ]]; then files=(*_scenes.py); fi
shift || true
for f in "${files[@]}"; do
  mod="${f%.py}"
  if [[ $# -gt 0 ]]; then scenes=("$@"); else
    scenes=($(python3 -c "import ast,sys;[print(n.name) for n in ast.parse(open(sys.argv[1],encoding='utf-8').read()).body if isinstance(n,ast.ClassDef) and n.name[:1]=='M']" "$f"))
  fi
  for s in "${scenes[@]}"; do
    echo ">> $f :: $s"
    "$MANIM" -qm --disable_caching --progress_bar none --media_dir "$MEDIA" "$f" "$s" >/dev/null
    src="$MEDIA/videos/$mod/720p30/$s.mp4"
    ffmpeg -v error -y -i "$src" -c:v libx264 -preset slow -crf 30 -pix_fmt yuv420p -movflags +faststart -an "$OUT/$s.mp4"
    d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT/$s.mp4")
    ffmpeg -v error -y -ss "$(python3 -c "print(float('$d')*0.6)")" -i "$OUT/$s.mp4" -frames:v 1 -vf scale=960:-1 -q:v 4 "$POS/$s.jpg"
    ls -lh "$OUT/$s.mp4" | awk '{print "   size:", $5}'
  done
done
