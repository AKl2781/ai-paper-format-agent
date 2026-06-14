# TODO

## 当前路线图 / Roadmap

### v0.6.3-real-demo-files

目标：补充脱敏真实 demo DOCX 和一次真实运行输出，让面试演示从“路径和案例说明”升级为“可直接复现的固定样本”。

计划：
- 放入脱敏后的待修改论文样本和模板样本。
- 使用推荐命名：`demo_inputs/messy_paper_sample.docx`、`demo_inputs/template_sample.docx`。
- 运行一次主流程，保留对应的 `formatted_result_sample.docx`、`report_sample.json`、`agent_trace_sample.json`。
- 记录样本来源、脱敏边界和不应承诺的能力边界。

状态：待处理。不得虚构样本或输出，必须基于真实可运行结果补充。

---

### v0.7-task-state

目标：为长流程 Agent 增加任务状态持久化 `task_state.json`，方便后续展示任务生命周期和异常恢复。

计划：
- 设计任务状态结构，例如 queued、running、succeeded、failed。
- 明确 `task_state.json` 与现有 `agent_trace` 的边界：前者描述任务生命周期，后者描述处理步骤。
- 保持 `/agent/run` 兼容，避免破坏现有前端和测试。
- 先写设计文档，再小范围实现。

状态：规划中。

---

### v0.8-trace-ui

目标：在前端可视化展示 `agent_trace`，让演示时能直接看到每一步处理状态、耗时和 fallback 信息。

计划：
- 设计结果页 trace 展示区域。
- 展示 `step`、`status`、`duration_ms`、`fallback_used`、`message`。
- 保持现有上传、预览、下载交互不变。
- 在实现前先确认 UI 方案和回归测试点。

状态：规划中。

---

## 下一阶段

### 在线预览优化

目标：提升最终 docx 在线预览的结构还原度和阅读体验。

状态：已完成（v0.3.2）

---

### 格式差异报告增强

目标：更清晰展示格式修改前后差异、实际修改段落数和处理项。

状态：已完成（v0.3.1）

---

### 参考文献检查

目标：增强参考文献标题、编号条目、尾部文献区和引用格式检查。

状态：已完成（v0.3.3）

---

### 图表编号检查

目标：检查图题、表题、编号连续性、单位和题注格式。

状态：已完成（v0.3.4）

---

### 真实论文测试库 / Real Paper Stress Test

目标：建立真实 DOCX 测试库和回归记录机制，验证 Agent 面对真实论文、报告、模板不匹配和复杂参考文献/图表编号场景时的稳定性。

状态：v0.5.1 稳定测试版已完成并冻结（v0.3.5 第一步已完成：已建立测试目录、manifest 占位清单、回归结果目录和测试计划；第二步已完成：已生成 10 个脱敏 DOCX 测试样本并更新 manifest；v0.4.6 已完成极端 DOCX 重复风险检测性能保护；v0.4.7.1 已完成 74.79MB 资源压力测试；v0.5.0 已新增批量回归脚本；v0.5.1 已完成 classification boundary warning 与 heavy_manifest.csv 压力回归接入；后续仅继续扩充样本库）

---

### [DONE] Resource Stress Test v0.4.7.1

目标：验证 30MB+ 大文档在上传、分类、格式修复、评分、预览、下载和 AI fallback 全链路中的稳定性。

状态：已完成（v0.4.7.1，`realistic_heavy_thesis.docx`：74.79MB、267 页、2489 段、80 张表、100 张唯一图片、300 条参考文献；完整 local Agent PASS，耗时 510.88s；预览、下载、AI fallback 和格式保真审计均 PASS）

---

### [DONE] 重复风险检测性能保护

目标：修复极端 DOCX 在重复风险检测阶段因段落两两相似度比较导致完整 Agent 超时的问题。

状态：已完成（v0.4.6，commit `af81c08`，tag `v0.4.6-repeat-risk-performance-guard`；`check_repeat_risk` 已增加最多 300 段采样、最多 30000 次比较硬上限、截断元数据和异常 fallback；普通 smoke、极端 DOCX 完整 local Agent、local `ai_score=null` / `ai_used=false` 均 PASS）

---

### [DONE] v0.4.9 repeat risk optimization

目标：优化 `plagiarism_checker` 性能，降低 74.79MB heavy DOCX 在重复风险检测阶段的耗时。

状态：已完成。`plagiarism_checker` before `196.741s -> 17.724s`，after `181.200s -> 17.928s`，合计 `377.941s -> 35.652s`；heavy local Agent `510.88s -> 51.209s`；py_compile、smoke、heavy DOCX、local `ai_score=null` / `ai_used=false`、预览和下载均 PASS。

---

### 标题正文混排

目标：识别并拆分段落开头或段落中间出现的编号标题与正文混排。

状态：已修复（已覆盖 `4.结语：正文` 和 `...办法。4. 结语：正文` 两类场景）

---

### Agent Orchestrator Layer

目标：把现有格式处理工具链包装为可解释智能体流程，记录计划、工具调用、决策、fallback、人工复查和规则置信度。

状态：已完成（v0.3.7，新增 `agent_trace` 顶层字段，旧前端兼容）

---

### Scoring Semantics Refinement

目标：统一格式规则分、风险稳定分、AI语言参考分和最终评分的展示语义，避免 AI 语言评分被误解为主评分。

状态：已完成（v0.4.1，新增 `score_breakdown` 语义字段，AI 分数仅作参考，不参与主评分）

---

### Beta 项目文档整理

目标：将项目整理为可展示、可运行、可说明的 beta 项目，包含 README、架构说明、Agent Trace、Risk Level、真实回归结果和部署规划。

状态：已完成（v0.4.0-beta-docs，仅新增/修改文档，未改业务代码）

---

### 学校模板库

目标：沉淀可复用的学校模板规则，减少每次上传模板的不确定性。

状态：待处理

---

### 批量真实样本回归脚本

目标：为 `test_documents/manifest.csv` 中的样本建立批量回归入口，统一记录分类、local/ai fallback、预览、下载、评分语义和性能耗时。

状态：已完成（v0.5.0）。新增 `paper-ai/backend/run_real_doc_regression.py`，支持读取 `manifest.csv` / `generated_manifest.csv`，按 case/category/limit 过滤运行，记录分类、Agent 状态、报告、预览、下载、local AI 字段、耗时和 small/medium/large 文件大小分桶；输出到 `regression_results/<run_id>/summary.csv`、`summary.json` 和 `cases/<case_id>.json`。不改变业务主链路。

---

### CNKI / GB/T 7714 真实来源入库规范

目标：明确 CNKI 期刊投稿库、公开投稿模板和 GB/T 7714 参考文献材料作为测试来源时的合法边界与入库流程。

状态：已完成（v0.5.0）。新增 `test_documents/CNKI_GBT7714_SOURCE_NOTES.md`，明确只使用公开或已授权文件，不纳入登录/付费/验证码/受限全文；真实论文必须脱敏；查重相关产品表述仍使用“重复风险检测”和“相似度预检”。

---

### 分类边界测试规则

目标：区分真实功能失败和可解释分类边界，避免 `lab_report` / `academic_paper` 混合结构样本误报为阻断级回归失败。

状态：已完成（v0.5.1 / real-doc-regression-boundary-pass）。`run_real_doc_regression.py` 已支持 `BOUNDARY_WARNING`，`generated_manifest.csv` 中 `reports_001/002/003` 已通过 `known_risks=classification_boundary` 标记；处理崩溃、输出缺失、报告缺失、预览/下载失败、local AI 字段异常仍计入 blocking FAIL。

---

### Heavy DOCX 压力回归接入

目标：将 30MB-100MB 大体积 DOCX 纳入真实文档回归体系，验证分类、local Agent、输出文件、修改报告、在线预览、下载和 local AI 字段稳定性。

状态：已完成（v0.5.1）。`realistic_heavy_thesis.docx` 已复制到 `test_documents/real/`，新增 `test_documents/heavy_manifest.csv`；本轮 local 回归 1/1 PASS，耗时 57.558s，输出 DOCX / 修改报告 / 预览 / 下载均通过，local `ai_score=null`、`ai_used=false`。

---

### [DONE] Performance Profiling v0.4.8

目标：拆分 74.79MB 重型 DOCX 完整 local Agent 的 510.88s 耗时分布，并将大文档处理时间优化到 120~150s。

状态：已完成。v0.4.8 已定位 Top1 瓶颈为 `plagiarism_checker`，before 196.741s，after 181.200s，合计 377.941s，占 heavy profiling 有效总耗时 92%+；v0.4.9 已完成对应优化。

---

### v0.5.0 Beta Readiness

目标：进入真实用户试用准备阶段，确认格式 Agent 在试用前的主流程、交付物和兼容性风险。

任务：
- 真实用户试用准备
- UI 流程检查
- 上传流程检查
- 下载流程检查
- 报告质量检查
- 文档兼容性检查

状态：已完成（v0.5.2 / beta-readiness-audit）。新增 `VERSION_0_5_2_BETA_READINESS_AUDIT.md`；本轮验收结果为 manifest 10/10 PASS、generated 21 PASS + 3 boundary warnings + 0 blocking FAIL、heavy 1/1 PASS、smoke PASS、frontend `npm run build` PASS。结论：可进入 controlled beta，但产品表述仍应定位为格式 Agent，不应包装为深度内容改写 Agent。

---

### 内容 Agent 段落级问题清单

目标：从当前词语级 AI 审校升级到段落级问题识别，输出口语化、主观化、逻辑跳跃、因果不清、关键词不规范和重复表达问题清单。

状态：待处理（在格式 Agent 稳定后推进）

---

### Controlled Beta 用户试用准备

目标：为第一轮 controlled beta 试用准备用户筛选、文档准入、试用任务、阻断标准、反馈表和退出条件。

状态：已完成（v0.5.3 / controlled-beta-trial-prep）。新增 `VERSION_0_5_3_CONTROLLED_BETA_TRIAL_PREP.md`；当前建议先收集 3-5 名可信用户的真实 DOCX 试用反馈，再决定 v0.5.4 优先做 UI polish、报告措辞修正或内容 Agent 窄能力。

---

### 准备试用用户说明和反馈表

目标：为 controlled beta 试用用户准备简单说明文档和反馈表，明确测试版边界、上传建议、支持能力、非承诺事项和问题反馈字段。

状态：已完成。新增 `BETA_TRIAL_USER_GUIDE.md` 和 `BETA_TRIAL_FEEDBACK_FORM.md`；说明当前是测试版、建议仅上传 `.docx`、先用备份副本测试、不上传隐私敏感或正式最终提交版论文、不承诺论文代写或生成正文，并收集文档类型、大小、页数、上传/生成/下载结果、修改评分、格式错乱、图片/表格丢失、报错、截图和继续试用意愿。
---

### [DONE] 暑期实习展示版整理

目标：在不大规模重构、不改变前端上传/预览/下载功能的前提下，增加统一调度层、标准化 Agent Trace、补充架构文档和开发记录。

状态：已完成。新增 `paper-ai/backend/services/agent_pipeline.py`，`/agent/run` 已通过统一调度层调用现有 `paper_agent`；`agent_trace` 已标准化为逐步列表，并保留旧解释型 trace 到 `agent_trace_detail`；顶层兼容 `modification_report`、`reference_check`、`figure_table_check`。本轮 `py_compile`、现有后端测试和 `npm run build` 均 PASS。
---

### v0.6.2 demo 样本整理

目标：准备 2-3 个适合面试演示的脱敏 DOCX 样本，覆盖标准论文、模板上传、参考文献提示、图表编号提示和 AI fallback 说明。

计划：

- 准备一个小型标准论文样本，控制处理耗时，适合现场演示。
- 准备一个带模板的样本，展示模板解析和通用规则 fallback 边界。
- 准备一个包含参考文献或图表编号轻微问题的样本，展示 `modification_report`、`reference_check`、`figure_table_check`。
- 为每个样本记录预期展示点和不应承诺的边界。

状态：待处理。仅整理样本和说明，不修改核心业务逻辑。

---

### v0.7 task_state

目标：为 Agent 长流程增加任务状态记录，方便后续支持更清晰的运行状态、错误恢复和前端进度展示。

计划：

- 设计 task 状态结构，例如 queued/running/succeeded/failed/requires_confirmation。
- 明确状态数据是否仅保存在内存或落盘，暂不默认引入数据库。
- 保持 `/agent/run` 兼容，避免破坏已有前端和测试。
- 将状态与现有 `agent_trace` 区分：task_state 说明任务生命周期，agent_trace 说明处理步骤。

状态：规划中。实现前需先写设计文档。

---

### v0.8 trace UI

目标：将后端 `agent_trace` 展示到前端 UI，让用户能看到每一步处理、耗时和 fallback 状态。

计划：

- 在结果页增加执行轨迹区域。
- 展示 `step`、`status`、`duration_ms`、`fallback_used`、`message`。
- 对 fallback 步骤做温和提示，例如“已使用通用规则”或“AI 不可用，已本地处理”。
- 保持原有上传、预览、下载交互不变。

状态：规划中。实现前需先确认 UI 方案和回归测试点。
