# 三板斧学习法 — 方法来源

## 原始出处

Ihtesham Ali (@ihtesham2005) 于 2026-03-07 发布的推文，讲述一位 MIT 研究生如何用 NotebookLM 在 48 小时内学完一学期课程。

## 三个核心提示词（原文）

### Prompt 1 — 抓框架
> "What are the 5 core mental models that every expert in this field shares?"

不是让 AI 列知识点，而是提炼**专家的思维结构**——拿到骨架。

### Prompt 2 — 找分歧
> "Where do the top 3 experts fundamentally disagree, and why?"

专家之间的分歧点 = 领域**最关键、最难、最有深度**的地方。

### Prompt 3 — 测真懂
> "Generate 10 questions that would separate someone who deeply understands this from someone who just memorized the textbook."

用来自测，答不上来就知道盲区在哪。

## 逻辑链

先搭骨架（心智模型）→ 再看争议（深水区）→ 最后自检（真懂 vs 假懂）

## 前置条件

原方法要求先一次性上传该领域的全部材料（教科书 + 论文 + 讲义），建立完整知识语料库。在 OpenClaw 中等价操作 = 先抓取所有资料内容到上下文窗口。

## 适用场景

- 快速入门一个新领域（48 小时突击）
- 系统学习一个主题（分批次，每批跑三板斧）
- 面试/考试前的深度复习
- 给团队做知识萃取和内训材料

## 不适用场景

- 需要动手实操的技能（如编程、设计）—— 三板斧只解决"理解"层面
- 资料本身质量太差或太少（垃圾进垃圾出）
