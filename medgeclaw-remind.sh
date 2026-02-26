#!/usr/bin/env bash
# medgeclaw-remind.sh — 快速重新注入 MedgeClaw 上下文
# 用途: openclaw 意外重置/新 session 丢失上下文时，快速恢复
# 用法: bash medgeclaw-remind.sh (在 MedgeClaw 项目目录下)

set -euo pipefail

MEDGECLAW_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$HOME/.openclaw/workspace"
CONFIG="$HOME/.openclaw/openclaw.json"

echo "🧬 MedgeClaw Quick Remind"

# 检查关键文件是否完整
needs_init=false

[ ! -f "$WORKSPACE/MEDGECLAW.md" ] && needs_init=true
! grep -q "MedgeClaw" "$WORKSPACE/IDENTITY.md" 2>/dev/null && needs_init=true
! python3 -c "
import json
with open('$CONFIG') as f:
    c = json.load(f)
dirs = c.get('skills',{}).get('load',{}).get('extraDirs',[])
assert any('MedgeClaw/skills' in d for d in dirs)
" 2>/dev/null && needs_init=true

if [ "$needs_init" = true ]; then
    echo "⚠️  配置不完整，运行完整初始化..."
    bash "$MEDGECLAW_DIR/medgeclaw-init.sh"
    exit 0
fi

# 一切正常，发送系统事件提醒 agent
echo "✅ 配置完整，发送提醒..."
openclaw system event --text "🧬 MedgeClaw 提醒: 你是 MedgeClaw，生物医药 AI 研究助手。项目在 $MEDGECLAW_DIR，详细配置见 MEDGECLAW.md 和 CLAUDE.md。遇到科研任务请参考 K-Dense Scientific Skills。" --mode now 2>/dev/null || true

echo "✅ Done."
