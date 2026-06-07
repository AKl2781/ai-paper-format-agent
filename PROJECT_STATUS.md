# 项目状态

当前版本号：v0.5.2 / beta-readiness-audit

项目名称：AI论文格式修改Agent

当前阶段：格式Agent（进行中）

完成度：

- 格式Agent：75%
- 内容Agent：30%
- 论文修改Agent：45%

说明：

- 格式Agent 已经具备可运行主链路：上传论文、可选模板、格式修复、评分、预览、下载。
- 内容Agent 仍处于早期：AI 模式能做少量词语级替换和语言评分，但不能稳定完成段落级润色、逻辑重组、主观化表达识别。
- 论文修改Agent 已有 Agent 流程雏形，但“真实内容修改能力”和“修改报告可信度”仍需增强。

# 已完成功能

- 文档分类：支持识别标准论文、课程作业、实验报告、简历、未知文档。
- 格式修复：支持标题、正文样式、字体、行距、缩进、页边距等基础格式修复。
- AI审校：支持 DeepSeek/OpenAI API；API 不可用时可降级到本地规则。
- 重复风险预检：支持相似段落、重复句子和重复风险等级检测。
- 在线预览：支持将最终 docx 转成 HTML 预览，并增强标题层级、参考文献区域和表格基础样式展示。
- 修改报告：支持输出修复项、评分对比、修改次数、未修复项、人工复查建议和格式差异摘要。
- 参考文献检查：支持识别参考文献章节、文末编号、正文引用、编号跳号、重复编号、正文引用缺失和文末未引用条目。
- 图表编号检查：支持识别图题、表题、Figure/Table 编号、编号跳号、重复编号和正文引用不存在的图表编号。
- 真实论文测试库：v0.3.5 第一步已建立 `test_documents/` 测试资产目录、`manifest.csv` 占位清单、`regression_results/` 结果目录和 `real_paper_test_plan.md` 测试计划；第二步已生成 10 个脱敏 DOCX 测试样本并更新 manifest。
- 批量真实样本回归脚本：v0.5.0 已新增 `run_real_doc_regression.py`，支持读取 `manifest.csv` / `generated_manifest.csv` 批量运行分类、local/ai Agent、报告、预览、下载和 local AI 字段校验，并输出 `summary.csv`、`summary.json` 与单 case JSON。
- CNKI / GB/T 7714 来源规范：v0.5.0 已新增 `test_documents/CNKI_GBT7714_SOURCE_NOTES.md`，明确只使用公开或已授权文件，不纳入登录/付费/验证码/受限全文；真实论文必须脱敏后才能进入测试库。
- Agent Orchestrator Layer：v0.3.7 已新增可解释智能体调度记录 `agent_trace`，记录 task_plan、tools_used、agent_decision、fallback_reason、manual_review_required 和 confidence，不改变原有处理结果。
- 评分语义：v0.4.1 已新增 `score_breakdown.format_score`、`risk_score`、`ai_language_score`、`final_score`、`score_confidence` 和 `score_explanation`，AI 语言评分仅作参考，不会拉低最终评分。
- 重复风险检测性能保护：v0.4.6 已为 `check_repeat_risk` 增加段落采样、比较次数硬上限和异常 fallback，极端 DOCX 不再因相似段落两两比较导致完整 Agent 超时。
- 资源压力测试：v0.4.7.1 已完成 74.79MB 重型 DOCX 全链路验证，覆盖上传、分类、local Agent、格式修复、评分、预览、下载和 AI fallback。
- 重复风险检测性能优化：v0.4.9 已优化 `plagiarism_checker`，在 `SequenceMatcher` 前加入段落长度差过滤、字符集合重叠率过滤、中文关键词重叠率过滤，并增加 `MAX_SEQUENCE_MATCHER_PAIRS=3000` 与 `REPEAT_RISK_TIME_BUDGET_SECONDS=25`，保持 `truncated/sampled_paragraphs/total_paragraphs/max_comparisons` 返回字段兼容。
- Beta 文档：v0.4.0-beta-docs 已整理 README 和 docs 文档，补充架构、Agent Trace、Risk Level、真实回归结果和部署规划说明。
- local模式：只执行本地格式修复和基础预检，返回 `ai_score=null`、`ai_used=false`。
- ai模式：在 local 格式修复基础上执行 AI/语言审校，返回 AI 语言参考评分和建议；主展示评分仍以格式规则分为准。

# 最近回归测试结果

最近一次完整回归结果：PASS。

PASS：

- Agent 能正常运行。
- 本地模式 local 正常：返回 `local_score`，`ai_score=null`，`ai_used=false`。
- AI模式 ai 正常：可运行完整流程；LLM 成功或 fallback 时不应中断主流程。
- local / template / ai fallback smoke test 全部 PASS。
- 标准论文弱结构样例不再被识别为 `unknown`。
- 标题正文混排已能拆分，例如 `4.结语：正文内容...`。
- 真实样本暴露的段落中间标题混排已修复，例如 `...办法。4. 结语：正文内容...` 会拆成前文、标题、正文三段。
- 上传模板后未再出现 `unsupported operand type(s) for *` 阻断错误。
- `C-51` 等异常模板残留已在 smoke test 中验证清理。
- 上传论文正常。
- 上传模板正常，模板缺失字段不会导致 Agent 直接崩溃。
- 不上传模板也可以启动 Agent。
- 在线预览正常：`/preview/{filename}` 返回 HTML。
- v0.3.2 在线预览优化已完成：增强标题层级、正文行距缩进、参考文献分区、表格样式和前端预览失败提示。
- 文件下载正常：`/download/{filename}` 返回 docx。
- 修改报告正常：包含 summary、before_after、change_counts、manual_review_items。
- v0.3.1 格式差异报告增强已完成：新增 format_diff_summary、changed_dimensions、score_delta_by_dimension、auto_fix_count、needs_manual_review_count。
- v0.3.3 参考文献检查已完成：新增 reference_check 字段，并将参考文献风险合并进人工复查项。
- v0.3.4 图表编号检查已完成：新增 figure_table_check 字段，并将图表编号风险合并进人工复查项。
- v0.3.5 Test Corpus 第一步已完成：新增真实论文测试库目录、脱敏说明、manifest 占位清单、回归结果目录和测试计划；未修改业务代码。
- v0.3.5 Test Corpus 第二步已完成：生成 clean、messy、references、figures_tables、template_mismatch 共 10 个脱敏 DOCX 测试样本，并更新 manifest；未修改业务代码。
- v0.3.7 Agent Orchestrator Layer 已完成：新增 agent_trace 顶层字段，用于解释 Agent 计划、工具调用、fallback 和人工复查判断；旧字段保持兼容。
- v0.4.1 Scoring Semantics Refinement 已完成：新增 score_breakdown 评分语义字段，保留 local_score/ai_score/ai_used 等旧字段，避免 AI 语言参考分造成“修完更低分”的误解。
- v0.4.6 Repeat Risk Performance Guard 已完成：提交 `af81c08`（tag: `v0.4.6-repeat-risk-performance-guard`）只修改 `paper-ai/backend/services/plagiarism_checker.py`，为重复风险检测增加最多 300 段参与比较、最多 30000 次相似度比较、`truncated/sampled_paragraphs/total_paragraphs/max_comparisons` 元数据和检测失败 fallback。
- v0.4.6 极端 DOCX 回归 PASS：`extreme_stress_test_thesis.docx` 完整 local Agent 返回 200，约 50.67s 完成，`status=ok`，评分 `78 -> 84`，预览和下载均 PASS，local 模式保持 `ai_score=null`、`ai_used=false`。
- v0.4.6 普通 smoke 回归 PASS：`test_smoke_agent_flow.py` 全部 PASS，覆盖分类、local、模板、AI fallback、预览和下载。
- v0.4.6 fallback 注入测试 PASS：重复风险检测异常时返回低风险占位结构，主流程不因相似度预检失败而中断。
- v0.4.7.1 Resource Stress Test 已完成：`realistic_heavy_thesis.docx` 大小 74.79MB，267 页，2489 段，80 张表，100 张唯一图片，300 条参考文献；分类为 `academic_paper`，置信度 0.90。
- v0.4.7.1 大文档 local Agent 回归 PASS：完整 local Agent 返回 200，`status=ok`，耗时 510.88s，评分 `81 -> 84`，local 模式保持 `ai_score=null`、`ai_used=false`。
- v0.4.7.1 接口与保真审计 PASS：预览接口返回 200，下载接口返回 200；输出文档保持 2489 段、80 张表、100 张图片和 300 条参考文献；图片数量、唯一性和可打开性均通过审计。
- v0.4.7.1 AI fallback 回归 PASS：模拟 AI 故障后主流程不中断，`language_review.mode=local`，耗时 479.86s。
- v0.4.9 Repeat Risk Performance Optimization PASS：`plagiarism_checker` before `196.741s -> 17.724s`，after `181.200s -> 17.928s`，合计 `377.941s -> 35.652s`；74.79MB heavy DOCX 完整 local Agent `510.88s -> 51.209s`；py_compile PASS，smoke PASS，local `ai_score=null` / `ai_used=false` PASS，预览 PASS，下载 PASS。
- v0.4.0-beta-docs 已完成：新增根目录 README 和 docs/ 文档，项目可展示、可运行、可说明。
- v0.5.0 批量真实样本回归入口已完成：新增 `run_real_doc_regression.py`，支持 small/medium/large 文件大小分桶、case/category/limit 过滤、非标准论文自动确认参数和 `regression_results/<run_id>/` 结果输出。
- v0.5.0 CNKI / GB/T 7714 来源规范已完成：新增公开/授权来源入库边界说明，禁止将登录、付费、验证码或授权受限的 CNKI 正文全文作为自动下载测试集。
- v0.5.0 批量回归脚本验证 PASS：`generated_manifest.csv --limit 2` 为 2/2 PASS；`manifest.csv` 完整 10 个样本为 10/10 PASS；`test_smoke_agent_flow.py` PASS。
- v0.5.1 / real-doc-regression-boundary-pass 已完成：`run_real_doc_regression.py` 支持区分 `BOUNDARY_WARNING` 与 blocking `FAIL`；`generated_manifest.csv` 中 3 个 `reports_*` hybrid 样本标记为 `classification_boundary`，不再计入阻断级 FAIL；generated 回归为 21 PASS + 3 boundary warnings + 0 blocking FAIL。
- v0.5.1 Heavy DOCX Stress Regression 已接入：`D:\新下载\realistic_heavy_thesis.docx` 已复制到 `test_documents/real/realistic_heavy_thesis.docx`，新增 `test_documents/heavy_manifest.csv`；74.79MB 样本 local 回归 PASS，耗时 57.558s，分类 `academic_paper`，输出 DOCX / 修改报告 / 预览 / 下载均通过，local `ai_score=null`、`ai_used=false`。
- v0.5.1 稳定测试版已冻结：新增 `VERSION_0_5_1_SUMMARY.md`；当前回归为 manifest 10/10 PASS、generated 21 PASS + 3 boundary warnings + 0 blocking FAIL、heavy 1/1 PASS、smoke PASS；建议 tag `v0.5.1-heavy-regression-pass`。
- v0.5.2 Beta Readiness Audit 已完成：新增 `VERSION_0_5_2_BETA_READINESS_AUDIT.md`；manifest 10/10 PASS、generated 21 PASS + 3 boundary warnings + 0 blocking FAIL、heavy 1/1 PASS、smoke PASS、frontend `npm run build` PASS；当前仍建议作为格式 Agent 做 controlled beta，不应包装为深度内容改写 Agent。
- `before_score` 和 `after_score` 正常返回。
- 首页 `http://127.0.0.1:3000` 返回 200。
- 核心接口无 404：`/health`、`/document/classify`、`/agent/run`、`/preview/{filename}`、`/download/{filename}`。
- 前端按钮不会因为 templateFile 为空、preview 为空、result 为空、document_type=unknown 而永久 disabled。

FAIL：

- 当前最新回归没有阻断级 FAIL。

Current Bottleneck：

- v0.5.2 已完成试用前 beta readiness audit，当前没有阻断级 FAIL；下一阶段可进入 controlled beta 用户试用准备，或选择一个窄范围内容 Agent 能力作为 v0.5.3 起点。

回归后仍需关注：

- AI模式实际内容修改量偏低。
- 修改报告对 AI 增强的表达可能强于实际改写效果。
- 参考文献识别仍可能偏弱。

# 当前已知Bug

## P0

- 当前没有阻断级 P0。
- Known High Risk：无阻断级风险。
- v0.4.9 已修复 74.79MB heavy DOCX 重复风险检测性能瓶颈，`plagiarism_checker` 合计耗时 `377.941s -> 35.652s`，完整 local Agent `510.88s -> 51.209s`；当前无阻断级性能风险。
- 已修复极端 DOCX 在重复风险检测阶段超时的问题：`check_repeat_risk` 已加入性能上限和 fallback，避免 1000+ 段文档触发不可控的两两 `SequenceMatcher` 比较。
- 已修复 standard paper 被识别为 `unknown` 的弱结构样例问题。
- 已修复标题正文混排：例如 `4.结语：正文内容...` 可拆成独立标题和正文。
- 已修复段落中间标题正文混排：例如 `...办法。4. 结语：正文内容...` 可拆成独立标题和正文。
- 已修复模板解析 `unsupported operand type(s) for *` 类阻断风险，模板异常时可 fallback。
- 已修复 `C-51` 等异常模板残留的基础清理规则。
- local / template / ai fallback smoke test 全部 PASS。

## P1

- AI内容评分可信度仍需提升：`ai_language_score` 已改为参考分，不参与主评分，但内容修改量与语言建议质量仍需继续增强。
- AI审校偏浅：当前主要是词语级替换，不能稳定完成段落级学术润色。
- 关键词规范不足：能修正“关键字/关键词”标签，但不能稳定规范关键词内容。
- 文档分类仍有边界问题：结构较弱、摘要/关键词/参考文献缺失的论文可能识别不稳定。
- 模板提取仍有限：复杂模板、目录、页眉页脚、脚注、图片题注、公式编号未完整处理。
- 修改报告可信度需增强：需要更明确区分格式修改、内容修改和 AI 实际改写。

## P2

- UI仍需优化：当前优先保证可用性，视觉和交互精细度还有提升空间。
- 前端中文文案和编码需要持续检查：PowerShell 中曾出现乱码显示，需保证文件按 UTF-8 保存。
- 仓库清理不足：uploads、outputs、日志、构建产物等容易污染长期上下文。
- 在线预览只保留基础结构，不追求 Word 完全还原。

# 当前风险

## 技术风险

- Word 文档格式复杂：python-docx 对目录、页眉页脚、批注、脚注、公式、图片题注等支持有限。
- AI输出不可控：LLM 可能返回非 JSON、空建议或过度改写，需要继续强化解析和保护策略。
- 评分系统解释风险已缓解：v0.4.1 已明确格式规则分、风险稳定分、AI语言参考分和最终评分；后续仍需继续绑定真实内容修改量。
- 文档分类存在误判风险：非标准论文、课程作业、实验报告和弱结构论文之间边界不稳定。
- 文件编码风险：中文文案在不同终端下可能显示乱码，后续修改需注意 UTF-8。
- 运行产物膨胀风险：uploads、outputs、`.next`、`node_modules`、日志文件会增加仓库体积和 AI 上下文成本。

## 产品风险

- 用户可能误以为 AI 已经深度修改论文内容，但当前主要能力仍是格式修复。
- 如果最终评分较高但内容改动很少，会损害用户信任。
- 修改报告如果没有展示真实改动量，会显得像“包装过度”。
- 非论文文档如果被强制套用论文格式，可能造成用户误解。
- 仅提供最终结果而缺少修改前后对照，会让用户难以判断 Agent 是否真的有效。

# 下一阶段目标

## 未来1周

- 在线预览优化（v0.3.2 已完成）。
- 格式差异报告增强（v0.3.1 已完成）。
- 参考文献检查（v0.3.3 已完成）。
- 图表编号检查（v0.3.4 已完成）。
- 学校模板库。

## 未来1个月

- 从格式Agent升级到内容Agent：
  - 系统识别口语化表达。
  - 系统识别主观化表达。
  - 系统识别情绪化表达。
  - 识别逻辑不通顺、观点跳跃、因果不清。
  - 识别关键词内容不规范。
  - 输出段落级问题清单。
- 从内容Agent升级到真正论文修改Agent：
  - 将修改分为安全自动修改、建议型修改、需要人工确认的修改。
  - AI评分绑定真实修改量和未解决问题数量。
  - 在线预览支持修改前后对照。
  - 修改报告明确展示“改了什么、没改什么、为什么没改”。
- 长期维护优化：
  - 清理运行产物。
  - 完善 `.gitignore`。
  - 保持 `AI_CONTEXT.md` 和 `PROJECT_STATUS.md` 随版本更新。
  - 每次功能变更后执行固定回归清单。
