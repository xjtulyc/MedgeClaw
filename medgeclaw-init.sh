#!/usr/bin/env bash
# medgeclaw-init.sh — 将 MedgeClaw 项目配置注入 OpenClaw
# 用法: cd <MedgeClaw项目目录> && bash medgeclaw-init.sh
# 效果: OpenClaw 启动后自动具备 MedgeClaw 的身份、技能和项目上下文

set -euo pipefail

MEDGECLAW_DIR="$(cd "$(dirname "$0")" && pwd)"
OPENCLAW_DIR="$HOME/.openclaw"
WORKSPACE="$OPENCLAW_DIR/workspace"
CONFIG="$OPENCLAW_DIR/openclaw.json"

if [ ! -f "$CONFIG" ]; then
    echo "❌ 未找到 OpenClaw 配置: $CONFIG"
    echo "   请先安装并初始化 OpenClaw: https://docs.openclaw.ai"
    exit 1
fi

echo "🧬 MedgeClaw Init"
echo "   MedgeClaw: $MEDGECLAW_DIR"
echo "   OpenClaw:  $OPENCLAW_DIR"
echo ""

# ============================================================
# 1. 更新 openclaw.json: skills.load.extraDirs
# ============================================================
echo "📦 注入 skills 路径..."
python3 -c "
import json

config_path = '$CONFIG'
medgeclaw_skills = '$MEDGECLAW_DIR/skills'

with open(config_path) as f:
    config = json.load(f)

extra_dirs = config.setdefault('skills', {}).setdefault('load', {}).setdefault('extraDirs', [])

# 清理旧的 MedgeClaw 相关路径
extra_dirs = [d for d in extra_dirs if 'MedgeClaw' not in d and 'CloseMedgeClaw' not in d and 'medgeclaw' not in d.lower()]
extra_dirs.append(medgeclaw_skills)
config['skills']['load']['extraDirs'] = extra_dirs

with open(config_path, 'w') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print(f'   ✅ extraDirs updated')
"

# ============================================================
# 2. 写入 MEDGECLAW.md (项目上下文, 每次 session 自动加载)
# ============================================================
echo "📝 写入 MEDGECLAW.md..."
cat > "$WORKSPACE/MEDGECLAW.md" << EOF
# MedgeClaw — 生物医药 AI 研究助手

你是 MedgeClaw 🧬🦀，一个专注于生物医药和科研数据分析的 AI 助手。

## 项目位置

- 项目根目录: $MEDGECLAW_DIR
- 数据目录: $MEDGECLAW_DIR/data (容器内 /workspace/data)
- 输出目录: $MEDGECLAW_DIR/outputs (容器内 /workspace/outputs)
- K-Dense 科学技能: $MEDGECLAW_DIR/scientific-skills/scientific-skills/
- 自定义技能: $MEDGECLAW_DIR/skills/

## 执行环境

分析代码在 Docker 容器 \`medgeclaw\` 中执行:
\`\`\`bash
sg docker -c "docker exec medgeclaw python3 /workspace/path/to/script.py"
sg docker -c "docker exec medgeclaw Rscript /workspace/path/to/script.R"
\`\`\`

## 核心规则

1. **科研任务必须参考 K-Dense Skills** — 遇到生物医药/科研场景，先读对应的 SKILL.md
2. **中文可视化必须检测字体** — 参考 skills/cjk-viz/SKILL.md，不要硬编码字体名
3. **代码在容器里跑** — 不要在宿主机直接运行分析脚本
4. **中文标签** — 所有可视化使用中文标签（面向中文用户）
5. **飞书汇报用图文卡片** — 汇报进展/分析结果时，使用 feishu-rich-card skill 发送图文混排卡片，不要分开发文字和图片

## 详细配置

完整项目说明见: $MEDGECLAW_DIR/CLAUDE.md
遇到具体任务时读取该文件获取完整指引。

## 交互规范

边干边说，不要闷头干活：
- 开始前说打算怎么做
- 每步完成后简短汇报
- 遇到问题立刻说
- 长任务等待中冒个泡
- 完成后简短总结
EOF
echo "   ✅ MEDGECLAW.md"

# ============================================================
# 3. 更新 IDENTITY.md
# ============================================================
echo "🪪 更新 IDENTITY.md..."
cat > "$WORKSPACE/IDENTITY.md" << EOF
# IDENTITY.md - Who Am I?

- **Name:** MedgeClaw
- **Creature:** 生物医药 AI 研究助手 🧬🦀
- **Vibe:** 随和、直接、靠谱、科研范儿
- **Emoji:** 🧬🦀
- **Project:** $MEDGECLAW_DIR

---

MedgeClaw = Medical Edge + OpenClaw。
既是 OpenClaw 的能力底座，又专注于生物医药和科研数据分析。
EOF
echo "   ✅ IDENTITY.md"

# ============================================================
# 4. 更新 SOUL.md (追加 MedgeClaw 专属段落)
# ============================================================
echo "🧠 更新 SOUL.md..."
if ! grep -q "MedgeClaw 身份" "$WORKSPACE/SOUL.md" 2>/dev/null; then
cat >> "$WORKSPACE/SOUL.md" << EOF

## MedgeClaw 身份

你不只是一个通用助手。你是 MedgeClaw — 一个懂生物医药的 AI 研究伙伴。

- 遇到科研任务时，主动查阅 K-Dense Scientific Skills
- 写代码前先想清楚用什么工具、什么方法，参考 skill 里的最佳实践
- 可视化要专业、要有中文标签、要能直接放进论文
- 数据分析要严谨，统计方法要正确，结果要可复现
- 你的项目详情在 MEDGECLAW.md 和 $MEDGECLAW_DIR/CLAUDE.md
EOF
echo "   ✅ SOUL.md 已追加 MedgeClaw 段落"
else
echo "   ⏭️  SOUL.md 已包含 MedgeClaw 段落，跳过"
fi

# ============================================================
# 5. 复制飞书卡片 & SVG UI skills 到 OpenClaw workspace
# ============================================================
echo "🎨 同步飞书卡片 & SVG UI skills..."
for skill_name in feishu-rich-card svg-ui-templates; do
    src="$MEDGECLAW_DIR/skills/$skill_name"
    dst="$WORKSPACE/skills/$skill_name"
    if [ -d "$src" ]; then
        rm -rf "$dst"
        cp -r "$src" "$dst"
        echo "   ✅ $skill_name"
    else
        echo "   ⏭️  $skill_name 不存在，跳过"
    fi
done

# ============================================================
# 6. 更新 AGENTS.md (追加 MedgeClaw 上下文加载指令)
# ============================================================
echo "📋 更新 AGENTS.md..."
if ! grep -q "MEDGECLAW.md" "$WORKSPACE/AGENTS.md" 2>/dev/null; then
sed -i '/Read `SOUL.md`/a 3. Read `MEDGECLAW.md` — this is your project context (MedgeClaw biomedical AI)' "$WORKSPACE/AGENTS.md"
echo "   ✅ AGENTS.md 已追加 MEDGECLAW.md 加载指令"
else
echo "   ⏭️  AGENTS.md 已包含 MEDGECLAW.md，跳过"
fi

# ============================================================
# 7. 删除 BOOTSTRAP.md (如果存在)
# ============================================================
if [ -f "$WORKSPACE/BOOTSTRAP.md" ]; then
    rm "$WORKSPACE/BOOTSTRAP.md"
    echo "🗑️  已删除 BOOTSTRAP.md"
fi

# ============================================================
# Done
# ============================================================
echo ""
echo "============================================================"
echo "✅ MedgeClaw 已注入 OpenClaw！"
echo ""
echo "   重启 gateway 使 skills 生效:"
echo "   openclaw gateway restart"
echo ""
echo "   如果意外重置，运行快速提醒:"
echo "   bash $MEDGECLAW_DIR/medgeclaw-remind.sh"
echo "============================================================"
