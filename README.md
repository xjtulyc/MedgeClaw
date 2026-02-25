# 🧬 MedgeClaw

**English** | [中文](#中文)

---

An open-source biomedical AI research assistant built on [OpenClaw](https://github.com/openclaw/openclaw) and [Claude Code](https://docs.claude.com/en/docs/claude-code/quickstart), integrating [140 K-Dense Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills) for bioinformatics, drug discovery, clinical research, and more.

**Talk to your research assistant via WhatsApp, Slack, or Discord → it runs the analysis → you view results in RStudio or JupyterLab.**

---

## Architecture

```
User (voice / text via WhatsApp · Slack · Discord)
        ↓
OpenClaw Gateway  (conversation layer)
        ↓  biomed-dispatch skill
Claude Code  (execution layer)
        ↓  K-Dense Scientific Skills (140 skills)
R + Python Analysis Environment
        ↓
RStudio Server :8787  +  JupyterLab :8888  (view results)
```

---

## What's Included

| Component                     | Description                                                                        |
| ----------------------------- | ---------------------------------------------------------------------------------- |
| **OpenClaw**                  | Conversational AI gateway — connects to your messaging apps                        |
| **Claude Code**               | Executes complex analysis workflows autonomously                                   |
| **K-Dense Scientific Skills** | 140 ready-to-use skills: genomics, drug discovery, clinical research, ML, and more |
| **R Environment**             | DESeq2, Seurat, edgeR, clusterProfiler, survival, ggplot2, and more                |
| **Python Environment**        | Scanpy, BioPython, PyDESeq2, lifelines, scikit-learn, and more                     |
| **RStudio Server**            | Browser-based R IDE at `localhost:8787`                                            |
| **JupyterLab**                | Browser-based Python/R notebooks at `localhost:8888`                               |
| **biomed-dispatch**           | The bridge skill that routes your requests to Claude Code                          |

---

## Prerequisites

- **Node.js 22+** — [nodejs.org](https://nodejs.org)
- **Docker + docker-compose** — [docs.docker.com](https://docs.docker.com/get-docker/)
- **Git**
- An API key from one of the supported model providers (see below)

---

## Quick Start

```bash
# 1. Clone with submodules (includes K-Dense Scientific Skills)
git clone --recurse-submodules https://github.com/xjtulyc/MedgeClaw
cd MedgeClaw

# 2. Run setup (creates .env template on first run)
bash setup.sh

# 3. Fill in your API key
nano .env

# 4. Run setup again to complete installation
bash setup.sh

# 5. Start the analysis environment
docker compose up -d

# 6. Start OpenClaw
openclaw onboard
```

Then open your messaging app and start talking to your assistant.

---

## Model Providers

Edit `.env` to choose your provider. All providers are drop-in replacements — no other changes needed.

| Provider                       | Base URL                             | Notes            |
| ------------------------------ | ------------------------------------ | ---------------- |
| **Anthropic Claude** (default) | `https://api.anthropic.com`          | Best quality     |
| **MiniMax 2.1**                | `https://api.minimax.chat/anthropic` | 国内可用，低延迟 |
| **GLM-4.7** (Z.ai)             | `https://api.z.ai/api/anthropic`     | 国内可用         |
| **DeepSeek**                   | `https://api.deepseek.com/anthropic` | 低成本           |
| **Ollama** (local)             | `http://localhost:11434/v1`          | 完全离线         |

---

## Usage Examples

Once OpenClaw is running, send messages like:

```
Analyze RNA-seq data at data/counts.csv vs data/meta.csv, treatment vs control
```
```
Search PubMed for recent papers on CRISPR base editing, summarize top 10
```
```
Run survival analysis on data/clinical.csv, time=OS_months, event=OS_status
```
```
Perform single-cell RNA-seq analysis on the 10X data in data/10x/
```
```
Virtual screen EGFR inhibitors from ChEMBL (IC50 < 50nM), generate SAR report
```

Results are saved to `./outputs/` and viewable in RStudio (`localhost:8787`) or JupyterLab (`localhost:8888`).

---

## Directory Structure

```
MedgeClaw/
├── docker/
│   ├── Dockerfile          # R + Python + RStudio + Jupyter
│   └── entrypoint.sh
├── skills/
│   └── biomed-dispatch/    # Core bridge skill
│       └── SKILL.md
├── scientific-skills/      # git submodule → K-Dense (140 skills)
├── data/                   # Put your data files here (git-ignored)
├── outputs/                # Analysis outputs appear here (git-ignored)
├── docker-compose.yml
├── setup.sh
├── .env.template
└── .gitmodules
```

---

## Updating K-Dense Scientific Skills

```bash
git submodule update --remote scientific-skills
```

---

## Contributing

Contributions welcome. The most valuable contributions are:

- Improvements to `skills/biomed-dispatch/SKILL.md` for better task routing
- New domain-specific skills in `skills/` (e.g., for specific clinical or lab workflows)
- Improvements to the Dockerfile (lighter image, newer package versions)

Please follow the [AgentSkills specification](https://agentskills.io/specification) for any new skills.

---

## License

MIT © 2026 [xjtulyc](https://github.com/xjtulyc)

This project bundles [K-Dense Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills) as a git submodule (MIT). Individual skills within that repository may have their own license — check each `SKILL.md` for details.

---

---

# 中文

**[English](#-medgeclaw)** | 中文

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

## 许可证

MIT © 2026 [xjtulyc](https://github.com/xjtulyc)

本项目以 git 子模块形式引入 [K-Dense Scientific Skills](https://github.com/K-Dense-AI/claude-scientific-skills)（MIT 协议）。该仓库中每个技能可能有独立许可证，使用前请查阅对应 `SKILL.md`。
