# Development Log

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
