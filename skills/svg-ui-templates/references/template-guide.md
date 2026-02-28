# SVG UI 模板参考手册

## 配色体系

所有模板基于 Material Design 色板，偏商务/学术风格：

| 模板 | 主色 | Header | 说明 |
|------|------|--------|------|
| list-panel | Indigo (#1A237E) | 深靛蓝 | 数据表格、列表展示 |
| checklist-panel | Teal (#004D40) | 深青 | 任务清单、进度追踪 |
| pipeline-status | Deep Purple (#311B92) | 深紫 | 流程依赖、状态图 |
| richtext-layout | Blue Grey (#263238) | 深灰蓝 | 图文混排、报告展示 |

### 状态色

| 状态 | 色值 | 用途 |
|------|------|------|
| 已完成 | #43A047 (Green 600) | 边框、文字、图标 |
| 进行中 | #FF8F00 (Amber 800) | 高亮边框、标签 |
| 待办 | #90A4AE (Blue Grey 300) | 低饱和边框 |
| 阻塞/错误 | #E53935 (Red 600) | 警告边框、虚线 |
| 信息/提示 | #1565C0 (Blue 800) | 指标卡片背景 |

### 字体栈

```
font-family: 'Inter', 'Helvetica Neue', 'Microsoft YaHei', sans-serif
```

中文回退到微软雅黑，保证 Windows/macOS/Linux 下均可正确渲染。

## 模板说明

### 1. list-panel.svg — 列表/表格面板

**适用场景：** 展示结构化数据列表、对比表、参数表等

**占位符：**
- `{{TITLE}}` — 标题
- `{{DATE}}` — 日期
- `{{SUBTITLE}}` — 副标题
- `{{COL_1}}` ~ `{{COL_4}}` — 列标题
- `{{ROW_N_COL_M}}` — 行数据（N=1-5, M=1-4）
- `{{SUMMARY}}` — 汇总行
- `{{FOOTER_NOTE}}` — 脚注

**扩展方法：** 复制 Row 块并 y 偏移 +56px，更新序号。调整 viewBox 高度。

### 2. checklist-panel.svg — 任务清单面板

**适用场景：** 任务清单、TODO 列表、项目检查点

**四种状态：**
- ✓ 已完成（绿色填充方框 + 删除线文字）
- ◐ 进行中（橙色边框 + 黄色高亮）
- □ 待办（灰色空方框）
- ✕ 阻塞（红色虚线边框 + 红色背景）

**占位符：**
- `{{TITLE}}`, `{{DATE}}`
- `{{DONE_COUNT}}`, `{{TOTAL_COUNT}}` — 完成数/总数
- `{{PROGRESS_WIDTH}}` — 进度条宽度（0-500）
- `{{PROGRESS_PERCENT}}` — 百分比
- `{{ITEM_1}}` ~ `{{ITEM_6}}` — 任务项
- `{{NOTE_1}}`, `{{NOTE_2}}` — 备注
- `{{FOOTER}}`

**扩展方法：** 复制 Item 块并 y 偏移 +60px。修改状态样式按需切换。

### 3. pipeline-status.svg — 流程依赖与状态图

**适用场景：** 任务执行流水线、阶段依赖关系、项目里程碑状态

**布局：** 上方横向流水线节点 + 下方详情卡片

**占位符：**
- `{{TITLE}}`, `{{DATE}}`
- `{{NODE_1}}` ~ `{{NODE_5}}` — 节点名称
- `{{NODE_N_OWNER}}` — 负责人
- `{{NODE_N_DURATION}}` — 周期
- `{{NODE_N_DEPS}}` — 依赖
- `{{NODE_N_OUTPUT}}` — 交付物
- `{{NODE_N_STATUS}}` — 状态
- `{{RISK_NOTE}}` — 风险提示
- `{{FOOTER}}`

**状态切换：** 修改节点 rect 的 fill/stroke 颜色和箭头 marker-end 引用。

### 4. richtext-layout.svg — 图文混排模板

**适用场景：** 带图片的报告、数据分析摘要、研究简报

**布局：** 左图右文 + 下方左文右图，含指标卡片行

**占位符：**
- `{{TITLE}}`, `{{DATE}}`, `{{SUBTITLE}}`
- `{{IMAGE_1_PLACEHOLDER}}`, `{{IMAGE_2_PLACEHOLDER}}` — 图片区域
- `{{IMAGE_1_CAPTION}}` — 图注
- `{{SECTION_1_TITLE}}`, `{{SECTION_1_LINE_1}}` ~ `{{SECTION_1_LINE_5}}`, `{{SECTION_1_NOTE}}`
- `{{SECTION_2_TITLE}}`, `{{SECTION_2_LINE_1}}` ~ `{{SECTION_2_LINE_4}}`
- `{{METRIC_1_LABEL}}`, `{{METRIC_1_VALUE}}` ~ `{{METRIC_4_LABEL}}`, `{{METRIC_4_VALUE}}`
- `{{FOOTER}}`, `{{PAGE_INFO}}`

**图片嵌入：** 将占位 rect 替换为 `<image>` 标签：
```xml
<image x="40" y="110" width="340" height="220" href="data:image/png;base64,..." clip-path="url(#imgClip1)" preserveAspectRatio="xMidYMid slice"/>
```

## 通用开发规范

1. viewBox 固定为 1200 宽（横屏 16:9 附近比例）
2. 所有卡片使用 `filter="url(#shadow)"` 统一阴影
3. 圆角统一：大卡片 rx=8，小元素 rx=4-6，胶囊按钮 rx=圆角半径
4. 文字层级：标题 20px bold → 区块标题 14-16px bold → 正文 13px → 注释 11-12px
5. 间距节奏：元素间距 16/24px，边距 40px
6. 转 PNG 命令：`python3 -c "import cairosvg; cairosvg.svg2png(url='input.svg', write_to='output.png', output_width=2400)"`
