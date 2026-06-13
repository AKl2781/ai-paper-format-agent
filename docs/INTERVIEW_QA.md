# 面试高频问答

版本：`v0.6.1-demo-polish`

本文档用于准备暑期实习面试。回答应基于当前已经实现的代码和测试，不夸大为 RAG、LangGraph、Milvus、数据库、用户系统或云部署项目。

## 1. 这个项目解决什么问题？

它解决的是 DOCX 论文/报告在提交前的格式整理和基础检查问题。用户上传论文后，系统自动做文档分类、格式修复、重复风险检测、参考文献检查、图表编号检查、修改报告生成、在线预览和下载。

当前项目定位是“格式 Agent”，不是论文代写工具，也不是正式查重系统。

## 2. 为什么说它是 Agent，而不是普通脚本？

它不是单个格式化脚本，而是一个有明确处理流程、状态记录、fallback 策略和报告输出的工具链：

- `agent_pipeline.py` 统一调度 `/agent/run`。
- `paper_agent.py` 串联分类、分析、模板、格式修复、AI/本地审校、重复风险检测和报告。
- `agent_trace` 记录每一步处理状态、耗时、fallback 和说明。
- `modification_report` 汇总自动处理和人工复查建议。

我没有让 LLM 自由规划流程，而是用稳定的工程规则调度工具，这更适合 DOCX 格式处理场景。

## 3. `agent_pipeline.py` 的作用是什么？

`agent_pipeline.py` 是 API 层和核心 Agent 之间的薄调度层。它不重写核心格式处理逻辑，主要负责：

- 调用 `paper_agent.run_paper_agent(...)`。
- 把旧解释型 trace 保留为 `agent_trace_detail`。
- 生成展示友好的 `agent_trace` 列表。
- 将 `after_analysis.reference_check` 和 `after_analysis.figure_table_check` 同步到顶层，保持旧字段兼容。

这样可以让 `/agent/run` 的返回更稳定，也方便面试展示和调试。

## 4. `agent_trace` 记录什么？

`agent_trace` 是逐步列表，每一项包含：

- `step`：处理步骤名称。
- `status`：步骤状态，例如 `ok`、`error`、`requires_confirmation`。
- `duration_ms`：步骤耗时。
- `fallback_used`：是否使用 fallback。
- `message`：可读说明。

例如未上传模板时，模板步骤会继续使用通用论文规则，并标记 `fallback_used=true`。

## 5. 为什么还保留 `agent_trace_detail`？

旧的解释型 trace 里有任务计划、工具调用、Agent 决策、fallback 原因、人工复查判断和置信度。它对调试和已有测试仍有价值。

新 `agent_trace` 更适合展示，旧 `agent_trace_detail` 更适合解释内部决策。两者同时保留，是为了兼容和降低回归风险。

## 6. local 模式和 ai 模式有什么区别？

local 模式只使用本地规则：

- 格式修复。
- 重复风险检测 / 相似度预检。
- 参考文献和图表编号检查。
- 本地评分和修改报告。

local 模式必须满足：

- `ai_score = null`
- `ai_used = false`

ai 模式会在格式修复后尝试 AI 语言审校。如果 LLM 调用失败，会 fallback 到本地语言规则，主流程继续。

## 7. AI 失败时系统怎么处理？

AI 是增强项，不是主流程唯一依赖。`language_reviewer.py` 会尝试调用 AI；如果失败，系统使用本地规则 fallback。

测试里有模拟 AI 失败的场景：`test_smoke_agent_flow.py` 会让 AI 调用抛异常，然后验证：

- `/agent/run` 仍返回 `status=ok`。
- 输出 DOCX 仍生成。
- 下载接口可用。
- `score_breakdown.ai_used=false`。

## 8. 评分是怎么避免被 AI 拉低的？

评分语义在 `docx_analyzer.py` 中做了区分：

- `format_score`：格式规则分。
- `risk_score`：风险稳定分。
- `ai_language_score`：AI 语言参考分。
- `final_score`：最终展示分。

AI 语言评分只作参考，不参与主评分计算，也不会拉低最终格式评分。`test_score_consistency.py` 覆盖了 AI 分数较低时最终分不下降的场景。

## 9. 参考文献检查具体检查什么？

当前检查包括：

- 是否识别到参考文献章节。
- 文末参考文献编号。
- 正文引用编号。
- 编号跳号。
- 重复编号。
- 正文引用缺失对应文献。
- 文末文献未被正文引用。

相关逻辑在 `docx_analyzer.py`，测试在 `test_reference_checker.py`。

## 10. 图表编号检查具体检查什么？

当前检查包括：

- 图题编号。
- 表题编号。
- Figure/Table 编号。
- 编号跳号。
- 重复编号。
- 正文引用了不存在的图表编号。
- Word 表格数量和表题数量不匹配时的提示。

相关测试在 `test_figure_table_checker.py` 和 `test_composite_numbering.py`。

## 11. 为什么不直接用 LangGraph 或更复杂的 Agent 框架？

这个项目的核心难点不是让 LLM 自由决策，而是稳定处理 DOCX 文件、保持接口兼容、处理 fallback、生成可解释报告。

当前阶段用显式 Python 工具链更合适：

- 可测试。
- 可控。
- 容易定位失败步骤。
- 不引入额外依赖和复杂运行环境。

未来如果要做多 Agent 或复杂任务状态，可以再评估框架，但当前没有为了包装概念而引入。

## 12. 为什么不接数据库？

当前流程是单次上传、单次处理、下载结果，主要运行产物在 `backend/uploads/` 和 `backend/outputs/`。没有用户系统、历史任务列表或多租户需求，所以暂时不接数据库。

后续 v0.7 计划做 `task_state`，那时可以考虑任务状态持久化，但这不是当前已实现功能。

## 13. 这个项目怎么保证没有破坏旧前端？

主要靠兼容字段和 smoke test：

- 保留 `modification_report`。
- 保留 `after_analysis.reference_check` 和 `after_analysis.figure_table_check`。
- 同步顶层 `reference_check`、`figure_table_check`。
- 保留 `steps`、`score_breakdown`、`download_url`、`filename`。
- `test_smoke_agent_flow.py` 覆盖上传、模板、local、ai fallback、预览、下载和新 trace 结构。

## 14. 你处理过哪些 Word 文档复杂性？

当前已处理或覆盖的点包括：

- 标题和正文基础样式。
- 行距、缩进、页边距。
- 标题正文混排拆分。
- 参考文献基础识别。
- 图表编号识别。
- 部分异常模板残留，例如 `C-51` 的清理在 smoke test 中覆盖。

但复杂 Word 对象仍有限制，例如目录、脚注、批注、公式、页眉页脚和复杂图文排版。

## 15. 重复风险检测是不是查重？

不是。项目中使用的表述是“重复风险检测”和“相似度预检”。它只用于提示相似段落和重复句子风险，不等同于知网、维普、万方或任何正式查重系统。

这是产品边界，也写在 README 和架构文档里。

## 16. 你最想展示的工程能力是什么？

我会强调四点：

- 把一个真实 DOCX 处理需求拆成可维护模块。
- 用 `agent_pipeline` 和 `agent_trace` 让流程可解释。
- 用 fallback 保护主流程稳定性。
- 用 smoke test 和模块测试守住上传、预览、下载、local、ai fallback 和兼容字段。

## 17. 当前最大不足是什么？

内容级修改能力还弱。AI 模式目前主要做语言审校建议和少量词语级替换，不能稳定完成段落级学术润色、逻辑重组或事实补写。

所以我会把项目定位为格式 Agent，而不是深度论文修改 Agent。

## 18. 下一步怎么迭代？

规划分三步：

- v0.6.2：准备更稳定的 demo 样本和演示素材。
- v0.7：引入 `task_state`，让长流程有更明确的任务状态记录。
- v0.8：把 `agent_trace` 做进前端 UI，让用户直接看到每一步处理过程。
