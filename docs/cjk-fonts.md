# CJK Fonts in Matplotlib

Rendering Chinese text in matplotlib is a common pain point, especially in Docker containers. This document covers the pitfalls and solutions implemented in MedgeClaw's `cjk-viz` skill.

## The `.ttc` Trap

**This is the #1 gotcha.**

Many Linux/Docker environments install CJK fonts as `.ttc` (TrueType Collection) files (e.g., `NotoSansCJK-Regular.ttc`). Matplotlib can detect these fonts, but `rcParams` settings often fail to render them.

### Symptoms

- `setup_cjk_font()` reports success
- `findfont()` locates the font file
- Chinese text still renders as boxes: □□□□

### Root Cause

Matplotlib's `rcParams['font.sans-serif']` font name matching doesn't work reliably with `.ttc` files. The font is registered in the font manager but not used during rendering.

### Solution: FontProperties Mode

For `.ttc` files, use `FontProperties(fname=path)` explicitly on every text element:

```python
from matplotlib.font_manager import FontProperties

CJK_FP = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')

# Every text element needs fontproperties=
ax.set_xlabel('中文标签', fontproperties=CJK_FP)
ax.set_ylabel('中文标签', fontproperties=CJK_FP)
ax.set_title('中文标题', fontproperties=CJK_FP)
ax.set_yticklabels(labels, fontproperties=CJK_FP)

# Legend requires special handling
ax.legend(title='图例标题', prop=CJK_FP)
ax.get_legend().get_title().set_fontproperties(CJK_FP)  # title is separate!

# suptitle too
plt.suptitle('总标题', fontproperties=CJK_FP)
```

### Priority Strategy

| Priority | Format | Method | Reliability |
|----------|--------|--------|-------------|
| 1 | `.ttf` / `.otf` | `rcParams` global setting | Best — set once, works everywhere |
| 2 | `.ttc` | `FontProperties(fname=)` per element | Reliable but verbose |
| 3 | None found | Install fonts first | N/A |

## Using the `cjk-viz` Skill

The `skills/cjk-viz/scripts/setup_cjk_font.py` helper handles all of this automatically:

```python
from setup_cjk_font import setup_cjk_font, get_cjk_fp

font_name = setup_cjk_font()   # detects and configures
CJK_FP = get_cjk_fp()          # get FontProperties object

# Use CJK_FP for all Chinese text
ax.set_title('标题', fontproperties=CJK_FP)
```

The helper:
1. Searches registered fonts for `.ttf`/`.otf` first (rcParams compatible)
2. Falls back to `.ttc` files with FontProperties mode
3. Scans `/usr/share/fonts`, `/usr/local/share/fonts`, `~/.local/share/fonts`
4. Prints a warning with install suggestions if nothing is found

### Diagnostics

Run the helper directly to diagnose your environment:

```bash
python3 skills/cjk-viz/scripts/setup_cjk_font.py
```

## Installing CJK Fonts in Docker

```bash
# Debian/Ubuntu
apt-get update && apt-get install -y fonts-noto-cjk

# After installing, clear matplotlib's font cache
python3 -c "
import matplotlib, shutil, os
cache = matplotlib.get_cachedir()
if os.path.exists(cache):
    shutil.rmtree(cache)
    print('Cache cleared:', cache)
"
```

## Font Candidates

The skill searches for these fonts in order:

| Font | Common Source |
|------|-------------|
| Noto Sans CJK SC | `fonts-noto-cjk` (Debian/Ubuntu) |
| Noto Sans SC | Google Fonts |
| Source Han Sans SC | Adobe |
| WenQuanYi Micro Hei | `fonts-wqy-microhei` |
| WenQuanYi Zen Hei | `fonts-wqy-zenhei` |
| Droid Sans Fallback | Android / older Docker images |
| SimHei | Windows |
| Microsoft YaHei | Windows |
| PingFang SC | macOS |
