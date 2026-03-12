# 🧠 Deep Learn — 三板斧深度学习

一个 [OpenClaw](https://github.com/openclaw/openclaw) Skill，用三个递进式提问快速掌握任意领域。

基于 MIT 研究生 48 小时学习法（[Ihtesham Ali](https://x.com/ihtesham2005)），将 NotebookLM 的学习方法论移植到 OpenClaw Agent 中。

## 方法论

给 Agent 喂入学习资料后，依次执行三个提问：

1. **🦴 心智模型** — 提炼 5 个该领域专家共享的核心思维结构
2. **🔥 专家分歧** — 找出 3 个顶尖专家之间的根本性分歧
3. **📝 深度自测** — 生成 10 道能区分"真懂"和"死记硬背"的题目

**逻辑链**：先搭骨架 → 再看争议（深水区）→ 最后自检

## 特性

- 📡 **多平台内容抓取** — 微信公众号、B站、YouTube、arXiv、小红书、X/Twitter、通用网页
- 🔄 **智能 Fallback** — 每个平台多级抓取策略，自动切换
- 📥 **五种输入方式** — 链接、文字、文件(PDF)、图片、纯主题（Agent 自动搜索）
- 📁 **结构化归档** — 学习报告 + 资料索引自动存档
- 🎯 **首次运行自动安装** — 无需手动配置依赖

## 安装

### 方式一：ClawHub（推荐）

```bash
clawhub install deep-learn
```

### 方式二：手动

```bash
git clone https://github.com/ZoezoeCookie/deep-learn.git
cp -r deep-learn ~/.openclaw/workspace/skills/
```

## 使用

安装后直接对 OpenClaw 说：

- *"帮我学习 Transformer 的工作原理"*
- *"用三板斧分析这几篇文章"* + 贴链接
- *"深度学习一下这个 PDF"* + 发文件

### 内容抓取脚本

也可以单独使用抓取功能：

```bash
# 检查/安装依赖
python3 scripts/smart_fetch.py --setup

# 抓取内容
python3 scripts/smart_fetch.py "https://mp.weixin.qq.com/s/xxx"
python3 scripts/smart_fetch.py "https://www.bilibili.com/video/BVxxx"
python3 scripts/smart_fetch.py "https://www.youtube.com/watch?v=xxx"

# 批量抓取并保存
python3 scripts/smart_fetch.py "<url1>" "<url2>" -o output.md
```

## 输出示例

```markdown
## 🧠 Prompt 1：五大核心心智模型

### 1.「一切皆压缩」模型
LLM 的本质是对互联网文本的有损压缩。405B 参数 ≈ 一个互联网的
zip 文件（有损版）。理解这一点，你就不会对幻觉感到惊讶...

## 🔥 Prompt 2：顶尖专家的根本分歧

### 分歧 1：Scaling 是否足够？
- **Sutton / Karpathy（Scaling 派）**：算力 + 数据 + 通用方法 = 持续进步...
- **3B1B（结构派）**：架构设计的精妙性不可替代...

## 📝 Prompt 3：10 道深度自测题
1. 为什么 LLM 在回答"草莓里有几个 r"时会出错，但在解微分方程时能答对？
```

## 文件结构

```
deep-learn/
├── SKILL.md                      # OpenClaw Skill 定义
├── README.md                     # 本文件
├── references/
│   └── method-origin.md          # 三板斧方法论来源
└── scripts/
    └── smart_fetch.py            # 智能内容抓取脚本
```

## 支持的平台

| 平台 | 抓取能力 | 备注 |
|------|---------|------|
| YouTube | ✅ 完整字幕 | 通过字幕 API 提取 |
| B站 | ✅ 简介 + 字幕 | 自动检测 YouTube 原版并提取字幕 |
| 微信公众号 | ✅ 全文 | Jina → Playwright 三级 fallback |
| arXiv | ✅ 摘要 + 全文 | 配合 Agent 的 PDF 工具 |
| 小红书 | ✅ 全文 | — |
| X/Twitter | ✅ 全文 | — |
| 通用网页 | ✅ 全文 | — |

## License

MIT
