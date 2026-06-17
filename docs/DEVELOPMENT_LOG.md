# Development Log

## 2026-06-18 v0.8.1-trace-ui-minimal

### 修改目标

在 `v0.7.3-task-state-cleanup` 稳定节点基础上，给前端结果页增加最小 Agent 执行过程展示：默认折叠展示 `agent_trace` 步骤列表，并展示 `task_id` / `task_state_path` 任务状态摘要。

### 修改范围

- 更新 `paper-ai/frontend/app/page.tsx`
  - 新增 `AgentTraceItem` 类型。
  - 在 `AgentResult` 中新增可选字段：`agent_trace`、`agent_trace_detail`、`task_id`、`task_state_path`。
  - 新增默认折叠的 `TracePanel`。
  - 展示 `agent_trace` 的 `step`、`status`、`message`、`duration_ms`、`fallback_used`。
  - 展示 `task_id` 和 `task_state_path` 摘要。
  - 不展示 `agent_trace_detail`。
  - 不读取 `task_state_path` 对应文件内容。
- 更新 `paper-ai/frontend/app/globals.css`
  - 新增 `trace-panel`、`trace-list`、`trace-state`、`trace-meta` 等局部样式。
  - 未改上传、预览、下载按钮样式。
- 更新 README、PROJECT_STATUS 和 TODO
  - 标记当前版本为 `v0.8.1-trace-ui-minimal`。
  - 说明当前只是最小前端 trace 展示和 task state 摘要展示。
  - 说明当前仍不是异步队列、完整 task state 可视化、完整断点续跑或完整工业级 Agent。

### 未修改范围

- 没有修改 `agent_pipeline.py`。
- 没有修改 `main.py`。
- 没有修改 `task_state.py`。
- 没有修改后端 smoke 测试断言。
- 没有修改 formatter/analyzer/language reviewer 核心业务逻辑。
- 没有修改上传、预览、下载主流程语义。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。
- 没有修改 demo 输入/输出样本文件。

### v0.8.1 验收说明

- `git status --short`：PASS，改动范围仅包含允许的前端文件和文档文件。
- `git diff --name-only`：PASS，未出现后端核心代码、依赖文件、demo 样本文件或测试断言改动。
- `npm run build`：PASS。
- `python paper-ai/backend/test_smoke_agent_flow.py`：PASS，local 模式仍保持 `ai_score=null`、`ai_used=false`，`agent_trace` 和 `task_state` 契约仍通过 smoke 校验。

## 2026-06-18 v0.7.3-task-state-cleanup

### 修改目标

在 `v0.7.2-task-state-sample` 稳定节点基础上，补充 task state 运行产物治理，避免 `paper-ai/backend/task_states/` 下的运行 JSON 污染 Git 工作区；同时补齐上轮只读检查发现的文档边界说明。

### 修改范围

- 更新 `.gitignore`
  - 新增 `paper-ai/backend/task_states/`。
  - 只忽略运行时 task state 目录。
  - 不影响 `demo_outputs/task_state_sample.json`，该文件仍作为固定 demo 样例保留在 Git 中。
- 更新 README
  - 标记当前版本为 `v0.7.3-task-state-cleanup`。
  - 补充当前不是完整工业级 Agent。
  - 说明 `task_states/` 是运行产物目录，`demo_outputs/task_state_sample.json` 是固定演示样例，两者不能混淆。
- 更新 `docs/ARCHITECTURE.md`
  - 补充 task state 运行产物与固定 demo 样例的区别。
- 更新 `docs/DEMO_SCRIPT.md` 和 `docs/DEMO_RESULT.md`
  - 补充 demo 样本不来自 CAJ 原文。
  - 保持“不来自真实用户论文、不用于论文代写”的边界说明。
- 更新 `PROJECT_STATUS.md` 和 `TODO.md`
  - 标记 v0.7.3 完成。
  - 将轻量清理函数或维护命令规划到 `v0.7.4-task-state-cleanup-function`。

### 未修改范围

- 没有修改 `task_state.py`。
- 没有修改 `agent_pipeline.py`。
- 没有修改 `main.py`。
- 没有修改前端页面交互。
- 没有修改测试断言。
- 没有修改 demo 输入/输出样本文件。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。

### v0.7.3 验收说明

- 本轮只修改 `.gitignore` 和 Markdown 文档。
- 未运行完整后端测试、smoke test 或 `npm run build`，原因是未修改 Python/前端业务代码、测试断言或依赖文件。
- 未运行 `py_compile`，原因是本轮未修改 Python 文件。
- 验收命令：`git status --short`、`git diff --name-only`、`git check-ignore paper-ai/backend/task_states/example.json`。

## 2026-06-18 v0.7.2-task-state-sample

### 修改目标

在 `v0.7.1-docs-sync-task-state` 稳定节点基础上，补充固定 `demo_outputs/task_state_sample.json`，并修复 `docs/DEMO_CASE.md` 中样本来源边界说明不够明确的问题。

### 修改范围

- 新增 `demo_outputs/task_state_sample.json`
  - 使用固定 `task_id=demo-task-state-sample`。
  - `status=succeeded`，`mode=local`。
  - `before_score=80`，`after_score=86`，与 `report_sample.json` 一致。
  - `ai_used=false`，`ai_score=null`，保持 local 模式语义。
  - `agent_trace_steps_count=9`，与 `agent_trace_sample.json` 一致。
  - `fallback_used=true`，来自当前 trace 样例中的 local AI 审校 fallback 标记。
  - 增加 `sample_note`，明确这是固定 demo 样例，不代表真实用户论文任务。
- 更新 `docs/DEMO_CASE.md`
  - 明确 demo 输入是人工构造 / 脱敏模拟样本。
  - 明确不来自真实用户论文，不来自 CAJ 原文，不用于论文代写。
  - 补充 `task_state_sample.json` 作为固定输出样例。
- 更新 `docs/DEMO_RESULT.md`、`docs/DEMO_SCRIPT.md`、README、PROJECT_STATUS 和 TODO
  - 同步 v0.7.2 状态。
  - 说明 `task_state_sample.json` 与 `agent_trace_sample.json` 的区别。
  - 保持当前仍不是异步队列、完整断点续跑或前端 task state 可视化的边界。

### 未修改范围

- 没有修改核心业务逻辑。
- 没有修改 `task_state.py`。
- 没有修改 `agent_pipeline.py`。
- 没有修改 `main.py`。
- 没有修改前端页面交互。
- 没有修改测试断言。
- 没有修改 demo 输入 DOCX、格式化输出 DOCX、report 样例或 agent trace 样例。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。

### v0.7.2 验收说明

- 本轮只新增固定 demo JSON 样例和 Markdown 文档。
- 未运行完整后端测试、smoke test 或 `npm run build`，原因是未修改 Python/前端业务代码、测试断言或依赖文件。
- 验收命令：`git status --short`、`git diff --name-only`、Python JSON 合法性和字段一致性检查。

## 2026-06-18 v0.7.1-docs-sync-task-state

### 修改目标

在 `v0.7.0-task-state-minimal` 稳定节点基础上，只同步文档，把 task state 最小任务状态持久化能力、边界和演示方式写清楚。

### 修改范围

- 更新 `README.md`
  - 补充 task state 是任务状态持久化雏形。
  - 说明每次 Agent Pipeline 运行会生成 `task_id`。
  - 说明 task state 记录 `status`、`input_files`、`output_files`、`duration_ms`、`fallback_used`、`error` 等信息。
  - 说明 `agent_trace` 记录处理步骤，`task_state` 记录任务生命周期。
- 更新 `docs/ARCHITECTURE.md`
  - 在架构图中加入 `task_state.py` 和 `task_states/{task_id}.json`。
  - 说明 `agent_pipeline.py` 调用 `task_state.py` 进行状态落盘。
  - 说明 `/agent/run` 同步返回仍保持兼容，只额外透出 `task_id` 和 `task_state_path`。
  - 说明 task state 不替代 `modification_report`、`reference_check`、`figure_table_check` 或 `agent_trace`。
- 更新 `docs/INTERVIEW_QA.md`
  - 新增 task state 与 agent_trace 区别、为什么不直接做异步队列、当前解决的问题和后续限制等问答。
- 更新 `docs/DEMO_SCRIPT.md`
  - 增加 task state 展示步骤。
  - 明确当前前端还没有 task state 可视化界面。
- 更新 `docs/DEMO_RESULT.md`
  - 说明 v0.7.0 后重新运行 demo 会生成 task state。
  - v0.7.1 当时明确记录了缺少固定 `demo_outputs/task_state_sample.json` 的缺口。
- 更新 `PROJECT_STATUS.md` 和 `TODO.md`
  - 标记当前版本和后续任务。

### 未修改范围

- 没有修改核心业务逻辑。
- 没有修改 `task_state.py`。
- 没有修改 `agent_pipeline.py`。
- 没有修改 `main.py`。
- 没有修改前端页面交互。
- 没有修改测试断言。
- 没有修改 demo 输入/输出样本文件。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。

### v0.7.1 验收说明

- 本轮只修改 Markdown 文档。
- 未运行完整后端测试、smoke test 或 `npm run build`，原因是未修改 Python/前端业务代码、测试断言或依赖文件。
- 验收命令：`git status --short`、`git diff --name-only`。

## 2026-06-17 v0.7.0-task-state-minimal

### 修改目标

在 `v0.6.3-real-demo-files` 稳定节点基础上，新增最小任务状态持久化能力。目标是记录每次 Agent 运行的生命周期状态，而不是把 `/agent/run` 改成异步队列，也不替代已有 `agent_trace`。

### 修改范围

- 新增 `paper-ai/backend/services/task_state.py`
  - 使用标准库生成 `task_id`。
  - 默认写入 `paper-ai/backend/task_states/{task_id}.json`。
  - 使用 UTF-8 JSON。
  - 使用临时文件加 `os.replace(...)` 写入，降低半写文件风险。
  - 记录 `running`、`succeeded`、`failed` 生命周期状态。
- 更新 `paper-ai/backend/services/agent_pipeline.py`
  - 在 pipeline 开始时创建 task state 并写入 `running`。
  - 成功返回前写入 `succeeded`。
  - 异常或内部 `status=error` 时写入 `failed`。
  - 结果中额外返回 `task_id` 和 `task_state_path`。
  - 保留原有返回字段语义和同步执行语义。
- 更新 `paper-ai/backend/test_smoke_agent_flow.py`
  - 校验 `/agent/run` 成功后存在 `task_id` 和 `task_state_path`。
  - 校验 task state 文件存在且 `status=succeeded`。
  - 校验 task state 包含 `input_files`、`output_files`、`duration_ms`。
  - 校验 local 模式仍保持 `ai_score=null`、`ai_used=false`。
  - 校验 `agent_trace` 仍为 list，下载字段仍可用。
  - 增加一个 direct pipeline 失败路径校验：不存在的 paper path 会写入 `status=failed` 和 `error`。
- 更新 `PROJECT_STATUS.md`、`TODO.md`、`README.md`
  - 记录当前版本、能力边界和后续任务。

### task_state 与 agent_trace 边界

- `task_state`：记录任务生命周期，例如 running、succeeded、failed、输入文件、输出文件、耗时、错误和评分摘要。
- `agent_trace`：记录处理步骤，例如识别文档类型、分析本地格式、模板解析、格式修复、AI 审校、重复风险预检、最终复查和报告生成。
- 本轮不做断点续跑，不做异步任务队列，不做前端进度条。

### 未修改范围

- 没有修改 formatter、analyzer、language reviewer 核心业务逻辑。
- 没有修改前端页面交互。
- 没有修改 `/agent/run` 的同步返回语义。
- 没有修改下载/预览逻辑。
- 没有修改 `package.json`、lock 文件或 `requirements.txt`。
- 没有修改 v0.6.3 demo 输入/输出样本文件。

### v0.7.0 测试结果

- `python -m py_compile paper-ai/backend/services/task_state.py paper-ai/backend/services/agent_pipeline.py paper-ai/backend/main.py`：PASS。
- `python test_reference_checker.py`：PASS。
- `python test_figure_table_checker.py`：PASS。
- `python test_risk_level_system.py`：PASS。
- `python test_composite_numbering.py`：PASS。
- `python test_formatter_mixed_heading.py`：PASS。
- `python test_score_consistency.py`：PASS。
- `python test_agent_orchestrator_trace.py`：PASS。
- `python test_smoke_agent_flow.py`：PASS，覆盖 task state 成功落盘和失败路径落盘。
- `npm run build`：SKIPPED。本轮未修改前端交互、前端依赖或前端页面代码。

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
