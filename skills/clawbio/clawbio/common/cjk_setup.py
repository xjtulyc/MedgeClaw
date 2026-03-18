#!/usr/bin/env python3
"""
CJK 字体自动检测与 matplotlib 配置 — 适配 MedgeClaw 环境

用法:
    from clawbio.common.cjk_setup import setup_cjk_font, get_cjk_fp
    font_name = setup_cjk_font()
    CJK_FP = get_cjk_fp()
    ax.set_xlabel('中文标签', fontproperties=CJK_FP)
"""

import os

CJK_FONT_CANDIDATES = [
    'Noto Sans CJK SC',
    'Noto Sans SC',
    'Source Han Sans SC',
    'WenQuanYi Micro Hei',
    'WenQuanYi Zen Hei',
    'Droid Sans Fallback',
    'AR PL UMing CN',
    'SimHei',
    'Microsoft YaHei',
    'PingFang SC',
    'STHeiti',
    'Hiragino Sans GB',
]

CJK_FILE_KEYWORDS = [
    'noto', 'cjk', 'hei', 'han', 'wenquan', 'droid',
    'source', 'fang', 'song', 'ming', 'yahei',
]

FONT_SEARCH_PATHS = [
    '/usr/share/fonts',
    '/usr/local/share/fonts',
    os.path.expanduser('~/.local/share/fonts'),
    os.path.expanduser('~/.fonts'),
]

_CJK_FONT_PATH = None
_CJK_FONT_NAME = None
_CJK_IS_TTC = False
_MPL_LOADED = False


def _ensure_mpl():
    """Lazy-load matplotlib to avoid import errors in environments without it."""
    global _MPL_LOADED
    if _MPL_LOADED:
        return
    import matplotlib
    matplotlib.use('Agg')
    _MPL_LOADED = True


def _find_in_registered(candidates):
    import matplotlib.font_manager as fm
    available = {}
    for f in fm.fontManager.ttflist:
        if f.fname.lower().endswith(('.ttf', '.otf')):
            available[f.name] = f.fname
    for name in candidates:
        if name in available:
            return name
    return None


def _find_in_filesystem(keywords, search_paths):
    import matplotlib.font_manager as fm
    from matplotlib.font_manager import FontProperties
    ttf_hits = []
    ttc_hits = []
    for base in search_paths:
        if not os.path.isdir(base):
            continue
        for root, _, files in os.walk(base):
            for f in files:
                fl = f.lower()
                if not any(k in fl for k in keywords):
                    continue
                path = os.path.join(root, f)
                if fl.endswith(('.ttf', '.otf')):
                    ttf_hits.append(path)
                elif fl.endswith('.ttc'):
                    ttc_hits.append(path)
    for path in ttf_hits:
        try:
            fm.fontManager.addfont(path)
            prop = FontProperties(fname=path)
            name = prop.get_name()
            if name:
                return name, path, False
        except Exception:
            continue
    for path in ttc_hits:
        try:
            prop = FontProperties(fname=path)
            name = prop.get_name()
            fm.fontManager.addfont(path)
            if name:
                return name, path, True
        except Exception:
            continue
    return None, None, False


def setup_cjk_font(candidates=None, extra_paths=None, verbose=False):
    """
    检测并配置 CJK 字体用于 matplotlib。
    Returns: 成功配置的字体名，或 None。
    """
    global _CJK_FONT_PATH, _CJK_FONT_NAME, _CJK_IS_TTC

    _ensure_mpl()
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    candidates = candidates or CJK_FONT_CANDIDATES
    search_paths = FONT_SEARCH_PATHS + (extra_paths or [])

    font_name = _find_in_registered(candidates)
    if font_name:
        plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans', 'sans-serif']
        plt.rcParams['axes.unicode_minus'] = False
        for f in fm.fontManager.ttflist:
            if f.name == font_name and f.fname.lower().endswith(('.ttf', '.otf')):
                _CJK_FONT_PATH = f.fname
                break
        _CJK_FONT_NAME = font_name
        _CJK_IS_TTC = False
        if verbose:
            print(f"CJK font configured (ttf, rcParams): {font_name}")
        return font_name

    font_name, font_path, is_ttc = _find_in_filesystem(CJK_FILE_KEYWORDS, search_paths)
    if font_name:
        _CJK_FONT_PATH = font_path
        _CJK_FONT_NAME = font_name
        _CJK_IS_TTC = is_ttc
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['font.sans-serif'] = [font_name, 'DejaVu Sans', 'sans-serif']
        if verbose:
            mode = "ttc, FontProperties" if is_ttc else "ttf, rcParams"
            print(f"CJK font configured ({mode}): {font_name} -> {font_path}")
        return font_name

    return None


def get_cjk_fp():
    """获取 CJK FontProperties 对象，用于 matplotlib fontproperties= 参数。"""
    from matplotlib.font_manager import FontProperties
    if _CJK_FONT_PATH:
        return FontProperties(fname=_CJK_FONT_PATH)
    return FontProperties()


def is_ttc_mode():
    """是否处于 .ttc FontProperties 模式。"""
    return _CJK_IS_TTC
