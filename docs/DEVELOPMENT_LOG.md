# Development Log

## 2026-06-17 v0.6.3-real-demo-files

### 修改目标

在 `v0.6.2-demo-samples` 稳定节点基础上，补充一组可用于面试演示的人工构造脱敏模拟 DOCX 输入样本、模板样本，以及一次 local 模式真实运行输出，让项目从“有 demo 样本目录说明”升级为“有可演示输入/输出样例”。

### 修改范围

- 新增 `demo_inputs/messy_paper_sample.docx`
  - 标题为“基于传感器数据分析的健康风险快速检测方法研究”。
  - 包含封面、中文摘要、英文摘要、关键词、正文 5 节、图表标题和参考文献。
  - 故意保留标题层级、正文缩进、行距、图表编号引用和参考文献编号检查点。
  - 内容为人工构造的脱敏模拟文本，不来自真实用户论文。
- 新增 `demo_inputs/template_sample.docx`
  - 包含一级标题、二级标题、正文、摘要、参考文献、图题和表题样式示例。
- 新增 `demo_outputs/formatted_result_sample.docx`
  - 由当前现有 `run_agent_pipeline(...)` local 模式处理生成。
- 新增 `demo_outputs/report_sample.json`
  - 保存本次运行的分类、评分、`score_breakdown`、`modification_report`、`reference_check`、`figure_table_check`、`repeat_risk` 等重点字段。
- 新增 `demo_outputs/agent_trace_sample.json`
  - 保存本次运行的逐步 `agent_trace`。
- 新增 `docs/DEMO_RESULT.md`
  - 记录 demo 输入/输出路径、故意设置的格式问题、运行方式、重点字段、限制和验收情况。
- 更新 `docs/DEMO_CASE.md`、`docs/DEMO_SCRIPT.md`、`README.md`
  - 将 demo 文件状态从推荐路径更新为当前已内置的模拟输入和 local 输出样例。
- 更新 `PROJECT_STATUS.md` 和 `TODO.md`
  - 标记当前版本和下一阶段任务。

### 未修改范围

- 没有修改核心业务逻辑。
- 没有修改 `agent_pipeline.py`。
- 没有修改 `/agent/run`。
- 没有修改 `paper_agent.py`。
- 没有修改 formatter、analyzer、language reviewer。
- 没有修改前端交互。
- 没有修改已有返回字段结构或测试断言。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。

### v0.6.3 运行与验收

- 基线检查：PASS
  - `git status --short` 初始为空。
  - `git log --oneline --decorate -5` 显示 HEAD 位于 `v0.6.2-demo-samples`。
- DOCX 输入生成：PASS
  - `messy_paper_sample.docx` 和 `template_sample.docx` 已生成。
- DOCX 结构检查：PASS
  - 三个 DOCX 均可通过 `python-docx` 打开并读取段落和表格。
- local 处理流程：PASS
  - 直接调用现有 `run_agent_pipeline(...)`，未启动常驻服务。
  - `status=ok`，`mode=local`，`classification.document_type=academic_paper`，`confidence=0.95`。
  - `before_score=80`，`after_score=86`。
  - local 模式保持 `ai_score=null`、`ai_used=false`。
- DOCX 渲染视觉 QA：SKIPPED
  - 当前环境缺少 LibreOffice/`soffice`，`render_docx.py` 无法生成 PNG。
- 完整后端测试、smoke test、前端构建：SKIPPED
  - 本轮只新增 DOCX/JSON/Markdown 演示资产与文档，未修改 Python/前端业务代码、测试断言或依赖文件。

## 2026-06-14 v0.6.2-demo-samples

### 修改目标

在 `v0.6.1-demo-polish` 稳定节点基础上，补充固定演示样本目录说明和面试演示案例文档，让项目更适合作为暑期实习面试展示材料。

### 修改范围

- 新增 `demo_inputs/README.md`
  - 说明演示输入样本目录用途。
  - 推荐待修改论文和模板文件命名：`messy_paper_sample.docx`、`template_sample.docx`。
  - 明确当前不虚构真实 DOCX 文件，后续可放入脱敏后的真实样本。
- 新增 `demo_outputs/README.md`
  - 说明演示输出结果目录用途。
  - 推荐输出文件命名：`formatted_result_sample.docx`、`report_sample.json`、`agent_trace_sample.json`。
  - 明确未真实运行前不声称这些输出已经生成。
- 新增 `docs/DEMO_CASE.md`
  - 固定面试演示案例说明，覆盖输入样本特征、处理流程、重点观察字段和 1 分钟讲解话术。
- 更新 `docs/DEMO_SCRIPT.md`
  - 在演示准备和演示输出部分补充推荐样本路径。
  - 明确这些路径是建议命名，不代表仓库已经内置真实样本。
- 更新 `README.md`
  - 标记当前版本为 `v0.6.2-demo-samples`。
  - 增加 Demo Samples / 演示样本说明。
- 更新 `PROJECT_STATUS.md` 和 `TODO.md`
  - 记录 v0.6.2 当前状态。
  - 将后续任务调整为 `v0.6.3-real-demo-files`、`v0.7-task-state`、`v0.8-trace-ui`。

### 未修改范围

- 没有修改核心业务逻辑。
- 没有修改 `agent_pipeline`。
- 没有修改 `/agent/run`。
- 没有修改 formatter、analyzer、language reviewer。
- 没有修改前端交互。
- 没有修改已有返回字段结构或测试断言。
- 没有修改依赖文件或 lock 文件。
- 没有新增真实 DOCX 文件或真实运行输出样本。

### v0.6.2 验收说明

- 本轮只修改 Markdown 文档和演示目录说明。
- 未运行完整后端测试、smoke test 或 `npm run build`，原因是未修改任何 Python/前端业务代码、测试断言或依赖文件。
- 验收命令：`git status --short`。

## 2026-06-14 v0.5.4-summer-internship-showcase

### 修改目标

将当前 AI论文格式修改Agent 整理为可展示版本，在不大规模重构、不改变前端上传/预览/下载功能的前提下，补齐统一调度层、标准化 trace 和架构说明。

### 修改范围

- 新增 `paper-ai/backend/services/agent_pipeline.py`
  - 作为 `/agent/run` 的统一调度层。
  - 调用现有 `paper_agent.run_paper_agent(...)`。
  - 标准化 `agent_trace`，每一步包含 `step`、`status`、`duration_ms`、`fallback_used`、`message`。
  - 保留旧解释型 trace 到 `agent_trace_detail`。
  - 将 `after_analysis.reference_check` 和 `after_analysis.figure_table_check` 同步为顶层兼容字段。
- 更新 `paper-ai/backend/main.py`
  - `/agent/run` 改为调用 `run_agent_pipeline(...)`。
  - 上传、预览、下载路由保持不变。
- 更新 `paper-ai/backend/services/paper_agent.py`
  - 为现有 `steps` 增加 `duration_ms` 和 `fallback_used`。
  - 标记非标准论文确认、未上传模板、模板 warning、local 跳过 AI、AI fallback 等场景。
- 更新 `paper-ai/backend/test_smoke_agent_flow.py`
  - 增加对新 `agent_trace` 列表结构的 smoke 校验。
  - 增加顶层 `reference_check`、`figure_table_check` 兼容字段校验。
- 更新 `docs/ARCHITECTURE.md`
  - 说明系统架构、处理流程、兼容字段和 fallback 策略。

### v0.5.4 测试结果

- `python -m py_compile`：PASS
- 现有后端测试：PASS
- `npm run build`：PASS
- 结论：上传处理主流程、local 模式、ai fallback、模板上传、预览、下载和兼容字段校验均通过 smoke test。

## 2026-06-14 v0.6.1-demo-polish

### 修改目标

将项目整理为暑期实习面试可展示版本。本轮只增强展示文档，不修改核心业务逻辑。

### 修改范围

- 更新 `README.md`
  - 补充项目定位、当前版本、功能、技术栈、处理流程、启动方式、测试命令和项目亮点。
  - 明确当前是格式 Agent，不是论文代写、正式查重或深度内容改写系统。
- 更新 `docs/ARCHITECTURE.md`
  - 补充 mermaid 架构图。
  - 说明 `agent_pipeline.py`、`agent_trace`、`agent_trace_detail`、local/ai fallback 和旧字段兼容。
- 新增 `docs/DEMO_SCRIPT.md`
  - 整理面试演示流程，包括开场介绍、架构讲解、上传主流程、trace 展示、fallback 说明和测试展示。
- 新增 `docs/INTERVIEW_QA.md`
  - 整理 18 个高频问答，覆盖 pipeline、trace、fallback、评分、参考文献、图表编号、兼容字段、测试覆盖和项目边界。
- 更新 `PROJECT_STATUS.md`
  - 标记当前版本为 `v0.6.1 / demo-polish`。
- 更新 `TODO.md`
  - 规划 `v0.6.2 demo 样本`、`v0.7 task_state`、`v0.8 trace UI`。

### 未修改范围

- 未修改核心业务逻辑。
- 未修改 formatter/analyzer/language reviewer。
- 未修改 `agent_pipeline` 核心执行逻辑。
- 未修改 `/agent/run` 接口行为。
- 未修改前端交互。
- 未修改已有返回字段结构。
- 未修改测试断言。
- 未修改依赖文件或 lock 文件。

### v0.6.1 测试结果

- `python -m py_compile`：PASS
  - 覆盖 `main.py`、`agent_pipeline.py`、`paper_agent.py`、`agent_orchestrator.py`、`document_classifier.py`、`docx_analyzer.py`、`docx_formatter.py`、`language_reviewer.py`、`plagiarism_checker.py`、`preview_service.py`、`template_extractor.py`。
- 现有后端测试：PASS
  - `test_reference_checker.py`
  - `test_figure_table_checker.py`
  - `test_risk_level_system.py`
  - `test_composite_numbering.py`
  - `test_formatter_mixed_heading.py`
  - `test_score_consistency.py`
  - `test_agent_orchestrator_trace.py`
- 主流程 smoke test：PASS
  - `test_smoke_agent_flow.py`
  - 覆盖上传处理主流程、local 模式、模板上传、AI fallback、预览、下载、`agent_trace`、`reference_check`、`figure_table_check`。
- `npm run build`：PASS
- 最终结论：PASS。v0.6.1 适合作为暑期实习面试展示文档版本；本轮没有修改核心业务逻辑。
