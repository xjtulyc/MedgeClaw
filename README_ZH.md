# 🧬 MedgeClaw

[English](README.md) | **中文**

---

基于 [OpenClaw](https://github.com/openclaw/openclaw) 和 [Claude Code](https://docs.claude.com/en/docs/claude-code/quickstart) 构建的开源生物医学 AI 研究助手，集成了 [K-Dense 140 个科学技能](https://github.com/K-Dense-AI/claude-scientific-skills)，覆盖生物信息学、药物发现、临床研究等领域。

**通过 WhatsApp、Slack 或微信发送指令 → 助手自动运行分析 → 在 RStudio 或 JupyterLab 中查看结果。**

---

## 架构

```
用户（语音/文字，通过 WhatsApp · Slack · Discord）
        ↓
OpenClaw 网关（对话层）
        ↓  biomed-dispatch skill
Claude Code（执行层）
        ↓  K-Dense 科学技能包（140 个）
R + Python 分析环境
        ↓
RStudio Server :8787  +  JupyterLab :8888（查看结果）
```

---

## 包含内容

| 组件                 | 说明                                                         |
| -------------------- | ------------------------------------------------------------ |
| **OpenClaw**         | 对话式 AI 网关，接入微信/Slack 等消息应用                    |
| **Claude Code**      | 自主执行复杂分析工作流                                       |
| **K-Dense 科学技能** | 140 个即用型技能：基因组学、药物发现、临床研究、机器学习等   |
| **R 环境**           | DESeq2、Seurat、edgeR、clusterProfiler、survival、ggplot2 等 |
| **Python 环境**      | Scanpy、BioPython、PyDESeq2、lifelines、scikit-learn 等      |
| **RStudio Server**   | 浏览器版 R IDE，访问 `localhost:8787`                        |
| **JupyterLab**       | 浏览器版 Python/R Notebook，访问 `localhost:8888`            |
| **biomed-dispatch**  | 核心桥接技能，将用户请求路由至 Claude Code                   |

---

## 环境要求

- **Node.js 22+** — [nodejs.org](https://nodejs.org)
- **Docker + docker-compose** — [docs.docker.com](https://docs.docker.com/get-docker/)
- **Git**
- 一个支持的模型提供商 API Key（见下方）

---

## 快速开始

```bash
# 1. 克隆项目（包含 K-Dense 子模块）
git clone --recurse-submodules https://github.com/xjtulyc/MedgeClaw
cd MedgeClaw

# 2. 运行安装脚本（第一次运行会生成 .env 模板）
bash setup.sh

# 3. 填入你的 API Key
nano .env

# 4. 再次运行安装脚本完成安装
bash setup.sh

# 5. 启动分析环境
docker compose up -d

# 6. 启动 OpenClaw
openclaw onboard
```

---

## 模型选择

编辑 `.env` 选择模型提供商，无需修改其他配置：

| 提供商                       | Base URL                             | 说明                   |
| ---------------------------- | ------------------------------------ | ---------------------- |
| **Anthropic Claude**（默认） | `https://api.anthropic.com`          | 效果最佳               |
| **MiniMax 2.1**              | `https://api.minimax.chat/anthropic` | 国内可用，低延迟       |
| **GLM-4.7**（智谱 Z.ai）     | `https://api.z.ai/api/anthropic`     | 国内可用               |
| **DeepSeek**                 | `https://api.deepseek.com/anthropic` | 低成本                 |
| **Ollama**（本地）           | `http://localhost:11434/v1`          | 完全离线，无需 API Key |

---

## ⚠️ 使用第三方 API 代理的注意事项

如果你使用第三方 API 代理（MiniMax、GLM、DeepSeek 或任何非 Anthropic 官方地址），**必须**在 `.env` 中配置 `ANTHROPIC_SMALL_FAST_MODEL`，否则 Claude Code 会卡死。

### 原因

Claude Code 在执行每条 Bash 命令前，会用一个轻量「小快模型」（默认 `claude-3-5-haiku`）做安全预检。大多数第三方代理不支持 Haiku，导致预检返回 503 错误，表现为无限卡在：

```
⚠️ [BashTool] Pre-flight check is taking longer than expected.
```

### 解决方法

在 `.env` 中添加：

```bash
# 第三方 API 代理必须设置：
ANTHROPIC_SMALL_FAST_MODEL=claude-sonnet-4-20250514  # 或你的代理支持的任意模型
```

然后重新运行 `bash setup.sh` 使配置生效。

### 验证方法

```bash
# 应在 30 秒内完成。如果卡住，说明 SMALL_FAST_MODEL 配置不对。
claude --dangerously-skip-permissions -p '运行: echo hello'
```

---

## 使用示例

OpenClaw 启动后，直接发送消息：

```
分析 data/counts.csv 的 RNA-seq 数据，treatment vs control，生成差异表达结果
```
```
搜索 PubMed 近两年 CRISPR 碱基编辑的文献，总结前 10 篇
```
```
对 data/clinical.csv 做生存分析，time=OS_months，event=OS_status
```
```
分析 data/10x/ 目录下的单细胞 RNA-seq 数据
```
```
从 ChEMBL 筛选 EGFR 抑制剂（IC50 < 50nM），生成构效关系报告
```

结果保存在 `./outputs/`，可在 RStudio（`localhost:8787`）或 JupyterLab（`localhost:8888`）中查看。

---

## 目录结构

```
MedgeClaw/
├── docker/
│   ├── Dockerfile          # R + Python + RStudio + Jupyter
│   └── entrypoint.sh
├── skills/
│   └── biomed-dispatch/    # 核心桥接技能
│       └── SKILL.md
├── scientific-skills/      # git 子模块 → K-Dense（140 个技能）
├── data/                   # 放置你的数据文件（不进 git）
├── outputs/                # 分析结果输出目录（不进 git）
├── docker-compose.yml
├── setup.sh
├── .env.template
└── .gitmodules
```

---

## 更新 K-Dense 科学技能

```bash
git submodule update --remote scientific-skills
```

---

## 参与贡献

欢迎贡献。最有价值的贡献包括：

- 改进 `skills/biomed-dispatch/SKILL.md`，提升任务路由准确性
- 在 `skills/` 下添加新的领域专属技能（如特定临床或实验室工作流）
- 优化 Dockerfile（减小镜像体积、更新包版本）

新技能请遵循 [AgentSkills 规范](https://agentskills.io/specification)。

---

## 开发路线图

- [x] 核心架构：OpenClaw + Claude Code + K-Dense 科学技能集成
- [x] Docker 分析环境（RStudio Server + JupyterLab）
- [x] 第三方 API 代理支持（`ANTHROPIC_SMALL_FAST_MODEL` 修复 BashTool 预检问题）
- [x] `CLAUDE.md` 项目规范（Claude Code 通过 docker exec 执行分析）
- [x] 多语言分析验证（Python + R，直接编写 + Claude Code + K-Dense skills）
- [ ] **多智能体工作流**：并行分发子分析任务（如 Python + R 同时跑），自动聚合结果并交叉验证
- [ ] **文献自动集成**：PubMed/bioRxiv 检索 → 自动生成引言和讨论章节，关联分析结果
- [ ] **交互式报告生成器**：从分析输出自动生成发表级别的 HTML/PDF 报告，含图表、统计叙述
- [ ] **领域专属技能链**：预置常见工作流流水线（GWAS → PRS → 孟德尔随机化，scRNA-seq → 轨迹分析 → 细胞通讯）
- [ ] **可复现引擎**：自动生成含冻结环境、数据校验和一键重跑的 Docker 复现包

---

## 许可证

MIT © 2026 [xjtulyc](https://github.com/xjtulyc)

本项目以 git 子模块形式引入 [K-Dense Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills)（MIT 协议）。该仓库中每个技能可能有独立许可证，使用前请查阅对应 `SKILL.md`。
