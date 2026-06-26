# TODO

## 当前路线图 / Roadmap

### [DONE] v0.6.3-real-demo-files

目标：补充人工构造的脱敏模拟 demo DOCX 和一次真实 local 模式运行输出，让面试演示从“路径和案例说明”升级为“可直接复现的固定样本”。

已完成：
- 已放入人工构造的脱敏模拟论文样本和模板样本。
- 已使用固定命名：`demo_inputs/messy_paper_sample.docx`、`demo_inputs/template_sample.docx`。
- 已通过现有 `run_agent_pipeline(...)` local 模式运行一次主流程，并保留 `demo_outputs/formatted_result_sample.docx`、`demo_outputs/report_sample.json`、`demo_outputs/agent_trace_sample.json`。
- 已在 `docs/DEMO_RESULT.md` 记录样本来源、故意设置的格式问题、运行方式、重点字段、限制和验收情况。

状态：已完成。样本不是真实用户论文，输出来自一次真实 local 模式处理流程。

---

### [DONE] v0.7.0-task-state-minimal

目标：为长流程 Agent 增加最小任务状态持久化 `task_state.json`，方便后续展示任务生命周期和异常恢复。

已完成：
- 新增 `paper-ai/backend/services/task_state.py`。
- task state 默认写入 `paper-ai/backend/task_states/{task_id}.json`。
- 已记录 `running`、`succeeded`、`failed` 生命周期状态。
- 已明确 `task_state.json` 与现有 `agent_trace` 的边界：前者描述任务生命周期，后者描述处理步骤。
- `/agent/run` 保持同步执行语义，旧字段兼容；仅额外透出 `task_id` 和 `task_state_path`。

状态：已完成。当前还不是断点续跑或异步队列。

---

### [DONE] v0.7.1-docs-sync-task-state

目标：同步 task state 文档说明，明确当前真实能力、字段、架构位置、演示方式和边界。

已完成：
- README 已补充 task state 能力说明。
- `docs/ARCHITECTURE.md` 已补充 `task_state.py` 和 `task_states/{task_id}.json`。
- `docs/INTERVIEW_QA.md` 已补充 task state 相关问答。
- `docs/DEMO_SCRIPT.md` 已补充 task state 演示步骤。
- `docs/DEMO_RESULT.md` 已在 v0.7.1 记录当时缺少固定 `task_state_sample.json` 的缺口；该缺口已在 v0.7.2 补齐。

状态：已完成。仅同步文档，未修改核心业务逻辑。

---

### [DONE] v0.7.2-task-state-sample

目标：为 `demo_outputs/` 补充一次固定 task state 输出样例，方便面试演示时直接查看。

已完成：
- 已保存固定样例 `demo_outputs/task_state_sample.json`。
- 样例字段与当前 `report_sample.json`、`agent_trace_sample.json` 的关键字段保持一致。
- 已更新 `docs/DEMO_CASE.md`，明确 demo 样本是人工构造 / 脱敏模拟，不来自真实用户论文，不来自 CAJ 原文，不用于论文代写。
- 已更新 `docs/DEMO_RESULT.md`、`docs/DEMO_SCRIPT.md`、README、PROJECT_STATUS 和开发记录。
- 没有把前端描述为已有 task state 可视化，也没有把系统描述为异步队列或完整断点续跑。

状态：已完成。

---

### [DONE] v0.7.3-task-state-cleanup

目标：为 `paper-ai/backend/task_states/` 增加轻量清理策略，避免运行产物长期膨胀。

已完成：
- 已在 `.gitignore` 中新增 `paper-ai/backend/task_states/`。
- 已明确 `paper-ai/backend/task_states/{task_id}.json` 是运行产物，不应提交。
- 已明确 `demo_outputs/task_state_sample.json` 是固定 demo 样例，应继续保留在 Git 中。
- 已补充 README、架构、演示脚本、demo 结果和项目状态说明。
- 未修改 `task_state.py`，未改变 `/agent/run` 同步语义。

状态：已完成。当前只做运行产物治理，尚未实现自动清理函数。

---

### v0.7.4-task-state-cleanup-function

目标：为 `paper-ai/backend/task_states/` 增加轻量清理函数或维护命令。

计划：
- 可选新增 `cleanup_task_states(task_states_dir, keep_latest=20)`。
- 只用标准库。
- 默认保留最近 20 个 task state JSON。
- 只删除 `task_states/` 目录内的 `.json` 文件。
- 不自动接入 pipeline，不改变当前 `/agent/run` 行为。

状态：规划中。

---

### [DONE] v0.8.1-trace-ui-minimal

目标：在前端结果页增加最小 Agent 执行过程展示，同时保持上传、预览、下载主流程不变。

已完成：
- 已在结果页增加默认折叠的 `agent_trace` 展示区域。
- 已展示 `step`、`status`、`duration_ms`、`fallback_used`、`message`。
- 已展示 `task_id` 和 `task_state_path` 摘要。
- 未读取 `task_state_path` 对应文件内容。
- 未展示 `agent_trace_detail`。
- 未修改后端核心 pipeline、`/agent/run` 同步语义或测试断言。

状态：已完成。当前只是最小前端展示，不是异步队列、完整 task state 可视化或完整断点续跑。

---

### [DONE] v0.8.2-trace-ui-polish

目标：优化 trace 展示文案、空状态和异常态，让 fallback 与失败状态更容易区分。

已完成：
- TracePanel 标题和说明已优化为“Agent 执行过程”，强调它是步骤级执行记录。
- `fallback_used=true` 已显示为“已使用 fallback / 本地规则兜底”，不表述为严重失败。
- `task_id` / `task_state_path` 摘要说明已补充“前端不会读取文件内容、不代表异步队列或任务恢复能力”。
- 已增加缺失 `message`、`duration_ms`、`status` 时的温和默认展示。
- 保持上传、预览、下载交互不变。

状态：已完成。当前只是展示体验打磨，不是完整 task state 可视化、异步队列或完整断点续跑。

---

### v0.8.3-demo-ui-check

目标：对 demo 输入输出和前端 TracePanel 做人工演示检查或截图检查，确认面试展示路径清晰。

计划：
- 使用 `demo_inputs/messy_paper_sample.docx` 和 `demo_inputs/template_sample.docx` 做一次人工演示检查。
- 确认结果页评分、报告、下载、预览和 TracePanel 展示不互相遮挡。
- 检查 fallback 文案、task state 摘要和缺字段状态是否容易解释。
- 如需截图验收，优先只记录检查结果，不修改核心流程。

状态：规划中。

---

### [DONE] v0.8.4-ui-polish-layout

目标：优化前端页面整体层次和演示观感，让页面更像正式工具产品，而不是功能堆叠页。

已完成：
- 上传论文、上传模板、模式选择和运行按钮已整理为更清晰的“开始处理”区域。
- 结果页已按结果总览、评分变化、修改报告、评分模块、检查结果、重复风险、Agent 执行过程、预览与下载组织。
- before_score / after_score 更醒目，并展示提升值、模式、AI 参考参与状态和任务 ID。
- TracePanel 仍默认折叠，只展示 `agent_trace` 和 `task_id` / `task_state_path` 摘要。
- 未读取 task state 文件内容，未展示 `agent_trace_detail`。
- 未修改后端核心 pipeline、`/agent/run` 同步语义、上传/预览/下载主流程或测试断言。

状态：已完成前端布局打磨。当前仍不是异步队列、完整 task state 可视化、完整断点续跑或完整工业级 Agent。

---

### [DONE] v0.8.5-ui-polish-details

目标：继续优化展示文案、空状态、小标签和细节样式。

已完成：
- 修复 390px 左右窄屏下的轻微横向溢出。
- 为页面根容器、主要卡片、按钮、TracePanel 和报告区域补充 `min-width: 0`、`max-width: 100%`、换行和小屏内边距规则。
- 窄屏下上传区、模式区、结果区、检查区和操作按钮会自然收敛，避免撑破 viewport。
- 长任务 ID、`task_state_path`、文件名和说明文字可自然换行。
- 未修改后端接口、核心 pipeline、上传/预览/下载主流程或测试断言。

状态：已完成。当前仍不是异步队列、完整 task state 可视化、完整断点续跑或完整工业级 Agent。

---

### [DONE] v0.8.6-template-runtime-cleanup

目标：治理 demo 上传模板后产生的后端模板运行副本，避免 `paper-ai/backend/templates/template_sample.docx` 这类未跟踪文件污染 Git 工作区。

已完成：
- 已删除当前未跟踪运行产物 `paper-ai/backend/templates/template_sample.docx`。
- 已在 `.gitignore` 中新增 `paper-ai/backend/templates/*.docx`。
- 已明确 `demo_inputs/template_sample.docx` 是固定 demo 输入样本，应继续被 Git 跟踪。
- 未修改后端核心逻辑、前端 UI、上传/预览/下载主流程或测试断言。

状态：已完成。当前只是运行产物治理，不是业务功能增强。

---

### v0.8.7-demo-ui-final-check

目标：重新使用 demo 输入文件做人工演示检查或截图检查，确认模板运行产物被忽略后，demo 后 Git 工作区仍保持干净。

计划：
- 使用 `demo_inputs/messy_paper_sample.docx` 和 `demo_inputs/template_sample.docx` 做人工演示。
- 检查上传、运行、评分、报告、TracePanel、预览、下载是否适合现场展示。
- 检查运行后 `git status --short` 不再出现 `paper-ai/backend/templates/template_sample.docx`。
- 只记录检查结果，除非发现明确展示问题或新的运行产物污染。

状态：规划中。

---

### [DONE] v0.9.0-ui-landing-redesign

目标：把前端首页从普通后台工具页升级为更适合演示的 AI SaaS 产品页 + 工具工作台 + 结果仪表盘风格。

已完成：
- 首屏已组织为 Hero、能力卡片、静态仪表盘预览和上传工作台。
- 上传论文、上传模板、模式选择和启动 Agent 的主流程语义保持不变。
- 结果区继续以 dashboard 形式展示评分变化、修改报告、参考文献检查、图表检查、TracePanel、预览和下载。
- TracePanel 仍默认折叠，只展示 `agent_trace` 步骤和 `task_id` / `task_state_path` 摘要。
- 未修改后端核心逻辑、`/agent/run`、测试断言、依赖文件或 demo 样本。

状态：已完成。当前仍不是异步队列、完整 task state 可视化、完整断点续跑或完整工业级 Agent。

---

### [DONE] v0.9.1-ui-run-flow-fix

目标：修复 v0.9.0 后完整 demo 检查中发现的页面点击运行 Agent 失败/错误提示过于笼统问题。

已完成：
- 已确认前端字段名与后端 `/agent/run` 字段一致：`paper`、`template`、`mode`、`allow_non_paper`。
- 已补充前端响应读取保护，支持读取 JSON、空响应和非 JSON 错误文本，避免真实错误被吞成笼统提示。
- 已补充分类型失败后的继续运行语义：当分类请求失败但用户继续运行时，向后端透传 `allow_non_paper=true`。
- 已通过浏览器真实点击 demo 流程验收：上传论文、上传模板、选择本地规则模式、点击运行、报告、TracePanel、预览和下载均可用。
- 未修改后端核心逻辑、UI 视觉布局、上传/预览/下载主流程语义或依赖文件。

状态：已完成。当前仍不是异步队列、完整断点续跑或完整工业级 Agent。

---

### v0.9.2-ui-final-demo-check

目标：重新做完整 demo 演示检查和截图检查，确认 v0.9.1 修复后桌面与窄屏都适合现场展示。

计划：
- 使用 `demo_inputs/messy_paper_sample.docx` 和 `demo_inputs/template_sample.docx` 做完整前端演示。
- 检查首屏、上传工作台、结果仪表盘、TracePanel、预览和下载。
- 检查 1440px 桌面和 390px 窄屏是否无横向溢出。
- 检查 demo 后 Git 工作区仍保持干净。

状态：规划中。

---

### v0.9.3-interview-demo-package

目标：整理面试展示包，把演示脚本、截图、固定 demo 输入输出和讲解重点合并成可复用材料。

状态：规划中。

---

### v1.0-demo-release-candidate

目标：准备演示候选版本，冻结当前可展示能力、边界说明和回归检查清单。

状态：规划中。

---

## 后续补充说明

- 如需完整 task state 可视化，需要后续新增安全读取接口，而不是让前端直接读取本地 `task_state_path`。

---

### v0.9-resume-draft

目标：设计断点续跑能力，但暂不默认实现完整异步队列。

计划：
- 梳理哪些步骤可重试、哪些步骤必须重新执行。
- 明确 `task_state`、`agent_trace`、输出文件之间的恢复关系。
- 先写设计文档，再决定是否实现。

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

### [DONE] v0.6.3 demo 文件整理

目标：准备适合面试演示的脱敏模拟 DOCX 样本，覆盖标准论文、模板上传、参考文献提示、图表编号提示和 local 输出说明。

已完成：

- 已准备一个小型模拟标准论文样本，适合现场演示。
- 已准备一个模板样本，展示模板解析输入。
- 已准备包含参考文献编号和图表编号引用检查点的样本，展示 `modification_report`、`reference_check`、`figure_table_check`。
- 已保存一次 local 模式输出样例，并记录预期展示点和不应承诺的边界。

状态：已完成（v0.6.3-real-demo-files）。仅整理样本和说明，未修改核心业务逻辑。

---

### [DONE] v0.7 task_state

目标：为 Agent 长流程增加任务状态记录，方便后续支持更清晰的运行状态、错误恢复和前端进度展示。

状态：已完成最小落盘版本（v0.7.0-task-state-minimal）、v0.7.1 文档同步、v0.7.2 固定 task state 样例和 v0.7.3 运行产物治理。后续清理函数见 `v0.7.4-task-state-cleanup-function`，断点续跑设计见 `v0.9-resume-draft`。

---

### [DONE] v0.8 trace UI

目标：将后端 `agent_trace` 展示到前端 UI，让用户能看到每一步处理、耗时和 fallback 状态。

已完成：

- 在结果页增加执行轨迹区域。
- 展示 `step`、`status`、`duration_ms`、`fallback_used`、`message`。
- 对 fallback 步骤做温和提示，不把 fallback 显示为严重失败。
- 展示 `task_id` 和 `task_state_path` 摘要，但不读取 task state 文件内容。
- 保持原有上传、预览、下载交互不变。
- 如后续需要完整 task state 可视化，应新增安全读取接口，而不是让前端直接读本地路径。

状态：已完成最小展示版本（v0.8.1-trace-ui-minimal）和展示打磨版本（v0.8.2-trace-ui-polish）。后续可进入 `v0.8.3-demo-ui-check` 或 `v0.9-resume-draft`。
