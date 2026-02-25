#!/bin/bash
set -e

echo "🧬 Biomed OpenClaw Setup"
echo "========================"

# ── Check dependencies ────────────────────────────────────────
command -v node >/dev/null || { echo "❌ Node.js 22+ required. https://nodejs.org"; exit 1; }
command -v docker >/dev/null || { echo "❌ Docker required. https://docs.docker.com/get-docker/"; exit 1; }

# Support both old standalone docker-compose and new docker compose plugin
if command -v docker-compose >/dev/null 2>&1; then
    COMPOSE_CMD="docker-compose"
elif docker compose version >/dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ docker compose required. https://docs.docker.com/get-docker/"; exit 1
fi

NODE_MAJOR=$(node -e "console.log(process.versions.node.split('.')[0])")
if [ "$NODE_MAJOR" -lt 22 ]; then
    echo "❌ Node.js 22+ required (current: $(node -v))"; exit 1
fi

# ── Fix npm global install permissions (no sudo needed) ───────
NPM_PREFIX="${HOME}/.npm-global"
if [ "$(npm config get prefix)" != "${NPM_PREFIX}" ]; then
    echo "🔧 Configuring npm to install globally to ${NPM_PREFIX} (no sudo needed)..."
    mkdir -p "${NPM_PREFIX}"
    npm config set prefix "${NPM_PREFIX}"
    SHELL_RC="${HOME}/.bashrc"
    if ! grep -q "npm-global" "${SHELL_RC}" 2>/dev/null; then
        echo "export PATH=\"${NPM_PREFIX}/bin:\$PATH\"" >> "${SHELL_RC}"
    fi
fi
export PATH="${NPM_PREFIX}/bin:${PATH}"

# ── .env ──────────────────────────────────────────────────────
if [ ! -f .env ]; then
    cp .env.template .env
    echo "📋 Created .env from template — please fill in your API keys:"
    echo "   nano .env"
    echo ""
    echo "   Then re-run: bash setup.sh"
    exit 0
fi

# ── Create workspace directories ─────────────────────────────
mkdir -p data outputs

# ── K-Dense Scientific Skills (git submodule) ─────────────────
if [ ! -f scientific-skills/README.md ]; then
    echo "📦 Initializing K-Dense Scientific Skills submodule..."
    git submodule update --init --recursive
fi

# ── Install OpenClaw ──────────────────────────────────────────
echo "🦞 Installing OpenClaw..."
npm install -g openclaw@latest

# ── Install Claude Code ───────────────────────────────────────
echo "🤖 Installing Claude Code..."
npm install -g @anthropic-ai/claude-code

# ── Configure Claude Code model provider ─────────────────────
source .env
mkdir -p ~/.claude

# Build the env block for Claude Code settings
CLAUDE_ENV='"ANTHROPIC_AUTH_TOKEN": "'"${ANTHROPIC_API_KEY}"'"'
CLAUDE_ENV="${CLAUDE_ENV}"$',\n    "ANTHROPIC_BASE_URL": "'"${ANTHROPIC_BASE_URL}"'"'
CLAUDE_ENV="${CLAUDE_ENV}"$',\n    "ANTHROPIC_DEFAULT_SONNET_MODEL": "'"${MODEL}"'"'
CLAUDE_ENV="${CLAUDE_ENV}"$',\n    "ANTHROPIC_DEFAULT_OPUS_MODEL": "'"${MODEL}"'"'
CLAUDE_ENV="${CLAUDE_ENV}"$',\n    "API_TIMEOUT_MS": "3000000"'

# If using a third-party proxy, set ANTHROPIC_SMALL_FAST_MODEL
# so Claude Code's BashTool pre-flight check uses a supported model
if [ -n "${ANTHROPIC_SMALL_FAST_MODEL:-}" ]; then
    CLAUDE_ENV="${CLAUDE_ENV}"$',\n    "ANTHROPIC_SMALL_FAST_MODEL": "'"${ANTHROPIC_SMALL_FAST_MODEL}"'"'
    echo "✅ ANTHROPIC_SMALL_FAST_MODEL set to: ${ANTHROPIC_SMALL_FAST_MODEL}"
elif [ "${ANTHROPIC_BASE_URL}" != "https://api.anthropic.com" ]; then
    echo "⚠️  WARNING: You are using a third-party API proxy (${ANTHROPIC_BASE_URL})"
    echo "   but ANTHROPIC_SMALL_FAST_MODEL is not set in .env."
    echo "   Claude Code may hang on bash commands!"
    echo "   Fix: add to .env:  ANTHROPIC_SMALL_FAST_MODEL=${MODEL}"
    echo ""
fi

cat > ~/.claude/settings.json <<EOF
{
  "env": {
    ${CLAUDE_ENV}
  }
}
EOF
echo "✅ Claude Code configured (model: ${MODEL})"

# ── Build Docker analysis environment ────────────────────────
echo "🐳 Building Docker analysis environment (this may take 10-20 min)..."
${COMPOSE_CMD} build

# ── Configure OpenClaw workspace ─────────────────────────────
mkdir -p ~/.openclaw
WORKSPACE_DIR="$(pwd)/openclaw-workspace"
mkdir -p "${WORKSPACE_DIR}/skills"

cp -r skills/biomed-dispatch "${WORKSPACE_DIR}/skills/"

# Write valid OpenClaw config (skills.load.extraDirs is the correct key)
SKILLS_DIR="$(pwd)/skills"
cat > ~/.openclaw/openclaw.json <<EOF
{
  "skills": {
    "load": {
      "extraDirs": ["${SKILLS_DIR}"]
    }
  }
}
EOF
echo "✅ OpenClaw workspace configured"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Reload shell:               source ~/.bashrc"
echo "  2. Start analysis environment: ${COMPOSE_CMD} up -d"
echo "     RStudio Server → http://localhost:8787  (user: rstudio, password: \$RSTUDIO_PASSWORD)"
echo "     JupyterLab     → http://localhost:8888  (token: \$JUPYTER_TOKEN)"
echo ""
echo "  3. Start OpenClaw:             openclaw onboard"
echo ""
echo "  4. Put your data files in:     ./data/"
echo "     Analysis outputs appear in: ./outputs/"