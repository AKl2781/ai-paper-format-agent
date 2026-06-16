# 面试演示脚本

版本：`v0.6.3-real-demo-files`

本文档用于暑期实习面试时演示 AI论文格式修改Agent。演示重点是“一个可运行、可解释、有 fallback、有测试覆盖的 DOCX 格式处理 Agent”。不要把它讲成论文代写、正式查重或深度内容生成系统。

## 0. 演示准备

内置输入样本路径：

- `demo_inputs/messy_paper_sample.docx`
- `demo_inputs/template_sample.docx`

已生成输出样例路径：

- `demo_outputs/formatted_result_sample.docx`
- `demo_outputs/report_sample.json`
- `demo_outputs/agent_trace_sample.json`

注意：

- 这些文件从 `v0.6.3-real-demo-files` 开始已经存在。
- 样本是人工构造的脱敏模拟文本，不来自真实用户论文。
- 输出样例由现有 local 模式处理流程生成，详见 `docs/DEMO_RESULT.md`。

## 1. 开场介绍，约 30 秒

可以这样说：

> 这个项目是一个基于 FastAPI 和 Next.js 的 AI论文格式修改Agent。用户上传 DOCX 后，系统会做文档分类、格式修复、重复风险检测、参考文献检查、图表编号检查、生成修改报告，并提供在线预览和下载。当前版本定位是格式 Agent，AI 只作为语言审校和参考评分，不承诺深度内容改写。

强调三点：

- 主链路完整：上传、处理、预览、下载。
- 流程可解释：每一步都有 `agent_trace`。
- 稳定性优先：AI 失败、模板缺失等情况都有 fallback。

## 2. 展示 README，约 1 分钟

打开 `README.md`，讲：

- 当前版本：`v0.6.3-real-demo-files`。
- 技术栈：FastAPI、python-docx、Next.js、TypeScript。
- 核心模块：`agent_pipeline.py`、`paper_agent.py`、`docx_formatter.py`、`docx_analyzer.py`、`language_reviewer.py`。
- Demo 样本：`demo_inputs/` 已放入模拟论文和模板，`demo_outputs/` 已保存一次 local 模式运行输出。
- 项目边界：不是 RAG，不是 LangGraph，不是 Milvus，不是数据库系统，不是论文代写。

可说：

> 我没有为了包装概念引入复杂框架，而是先把 DOCX 处理主链路做稳定，把流程、fallback、测试和演示路径补齐。

## 3. 展示架构图，约 2 分钟

打开 `docs/ARCHITECTURE.md`，展示 mermaid 图。

讲解顺序：

1. 前端只负责上传、展示结果、预览和下载。
2. `main.py` 是 API 层。
3. `agent_pipeline.py` 是统一调度层，负责包装核心 Agent 和标准化 trace。
4. `paper_agent.py` 串联真正的业务工具。
5. `docx_formatter.py` 修改 Word 格式。
6. `docx_analyzer.py` 做评分、参考文献、图表编号检查。
7. `language_reviewer.py` 处理 AI/本地语言审校 fallback。

可说：

> 我把“调度”和“核心处理”拆开，是为了让接口输出稳定，并且不把格式修复逻辑和展示层 trace 混在一起。

## 4. 演示固定案例，约 3 分钟

参考 `docs/DEMO_CASE.md`。

内置样本特征：

- 标题格式不统一。
- 正文缩进或行距不规范。
- 参考文献编号存在可检查点。
- 图表编号和正文图号引用存在可检查点。

演示步骤：

1. 打开前端页面。
2. 上传论文 DOCX。推荐路径：`demo_inputs/messy_paper_sample.docx`。
3. 可选上传模板 DOCX。推荐路径：`demo_inputs/template_sample.docx`。
4. 选择 `local` 模式或 `ai` 模式。
5. 启动 Agent。
6. 展示执行步骤、评分、修改报告。
7. 展示在线预览。
8. 下载最终 DOCX。

讲解重点：

- 未上传模板时走通用论文规则 fallback。
- local 模式必须返回 `ai_score=null`、`ai_used=false`。
- 修改报告说明改了什么、还有哪些人工复查建议。

## 5. 演示 agent_trace，约 2 分钟

在浏览器 Network 面板或后端返回 JSON 中展示 `agent_trace`。

说明每一项：

- `step`：当前处理步骤。
- `status`：步骤状态。
- `duration_ms`：耗时。
- `fallback_used`：是否使用 fallback。
- `message`：给用户或开发者看的简短说明。

当前已保存输出样例：

- `demo_outputs/agent_trace_sample.json`

可说：

> 这个 trace 不是为了炫技，而是为了让 Agent 不像黑盒。出了问题时，我能知道卡在分类、模板、格式修复、AI 审校还是报告生成。

## 6. 演示报告和输出，约 2 分钟

重点观察：

- `modification_report`
- `reference_check`
- `figure_table_check`
- `before_score`
- `after_score`
- `download_url`

当前已保存样例：

- `demo_outputs/formatted_result_sample.docx`
- `demo_outputs/report_sample.json`

注意：这些文件由 `v0.6.3` 的 local 模式真实运行生成；不要把它讲成 AI 深度内容改写结果。

## 7. 演示 ai fallback，约 1 分钟

不一定现场调用真实 LLM，可以讲 smoke test 里已经覆盖：

- 模拟 AI 调用失败。
- `/agent/run` 仍返回 `status=ok`。
- `score_breakdown.ai_used=false`。
- 下载文件仍生成。

可说：

> 我把 AI 当成增强项，不当成主流程唯一依赖。所以 AI 不可用时，用户仍然能拿到本地格式修复结果。

## 8. 展示测试，约 2 分钟

展示命令，不建议现场全部跑很久；如果面试允许，可以跑 smoke 或说明已经验收。

推荐说明：

```powershell
cd D:\ai_论文修改格式\paper-ai\backend
python test_smoke_agent_flow.py
```

测试覆盖点：

- 文档分类。
- local 主流程。
- 模板上传。
- AI fallback。
- 预览接口。
- 下载接口。
- `agent_trace` 结构。
- `reference_check`、`figure_table_check` 兼容字段。

## 9. 项目边界说明，约 30 秒

主动说明限制会更可信：

- 当前不是正式查重，只做重复风险检测 / 相似度预检。
- 当前不是论文代写，不生成实验结果或参考文献。
- 复杂 Word 对象支持有限，例如目录、脚注、公式、页眉页脚。
- AI 评分只是参考，不参与主评分，不会拉低格式规则分。
- 当前 v0.6.3 已内置人工构造的脱敏模拟 DOCX 样本和一次 local 模式输出样例，但尚未做 Word 渲染截图验收。

## 10. 收尾，约 30 秒

可以这样总结：

> 这个项目的重点不是堆 AI 名词，而是把一个 DOCX 格式处理需求做成稳定的 Agent 工程：有清晰模块、有 fallback、有兼容字段、有 trace、有测试。v0.6.3 已经补齐一组可演示的模拟 DOCX 输入、模板和 local 输出样例，下一步会推进任务状态和 trace UI。

## 11. 常见演示风险

- 不要上传隐私敏感或正式提交论文。
- 不要承诺“查重通过”。
- 不要承诺“AI 深度润色整篇论文”。
- 如果 AI API 没配置，直接解释 fallback 设计。
- 不要把内置模拟样本说成真实用户论文。
- 如果预览样式与 Word 不完全一致，说明预览是结构化 HTML，不是像素级还原。
