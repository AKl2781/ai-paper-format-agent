# Interview Demo Package

版本：`v0.9.4-demo-screenshot-package`

本文档用于面试和项目演示。它整理当前稳定演示代码基线 `v0.9.2-ui-fetch-compat-fix` 的讲解话术、演示流程、技术架构、亮点、边界和常见追问。v0.9.4 进一步补充截图/录屏素材指南，方便准备 README、简历附件、作品集和答辩 PPT。当前项目定位是论文格式 Agent，不是论文代写工具、正式查重系统或完整工业级 Agent。

## A. 项目一句话介绍

这是一个面向高校论文模板的 AI 论文格式审查与自动排版 Agent，支持上传论文和模板，输出格式化 DOCX、评分变化、修改报告、参考文献/图表检查、Agent Trace 和任务状态摘要。

## B. 30 秒介绍

这个项目用 FastAPI + Next.js 做了一个可运行的 DOCX 论文格式 Agent。用户上传论文和可选模板后，后端会完成文档分类、模板规则提取、格式修复、重复风险预检、参考文献检查、图表编号检查，并返回修改报告、评分变化、在线预览和下载链接。它的重点不是论文代写，而是把格式审查、模板对齐、报告生成和 Agent 执行过程可观测做成一条稳定工程链路。

## C. 2 分钟演示流程

1. 打开前端页面：`http://127.0.0.1:3000`。
2. 上传 demo 论文：`demo_inputs/messy_paper_sample.docx`。
3. 上传 demo 模板：`demo_inputs/template_sample.docx`。
4. 自动化演示时可先复制到 ASCII 临时路径，例如 `C:\Temp\paper-ai-demo\`，避免中文路径下浏览器自动化文件句柄异常。
5. 选择本地规则模式。
6. 点击启动 Agent。
7. 展示评分变化：`80 -> 86`。
8. 展示 `Agent修改报告`：自动处理、变化维度、人工复查项。
9. 展示 `reference_check`：参考文献重复编号、跳号、未引用条目。
10. 展示 `figure_table_check`：正文引用图号不存在等检查点。
11. 展开 TracePanel，说明 9 个步骤、耗时、fallback 和 message。
12. 展示 `task_id` / `task_state_path` 摘要，强调前端不读取 task state 文件内容。
13. 展示在线预览。
14. 点击下载最终 DOCX。

v0.9.2 final demo check 已通过：`npm run build` PASS，真实页面 demo PASS，`/document/classify` 200，`/agent/run` 200，preview/download PASS，TracePanel PASS，桌面和 390px 窄屏无横向溢出，demo 后 `git status` 干净。

## D. 技术架构讲法

- 前端：Next.js + React + TypeScript，负责上传、模式选择、结果 dashboard、TracePanel、预览和下载。
- 后端：FastAPI，提供 `/document/classify`、`/agent/run`、`/preview/{filename}` 和 `/download/{filename}`。
- DOCX 解析与格式化：基于 `python-docx`，围绕段落、标题、行距、缩进、页边距和样式规则做处理。
- `template_extractor`：从上传模板中提取可用格式规则，缺失或不完整时 fallback 到通用论文规则。
- `docx_formatter`：执行标题、正文、段落和页面基础格式修复。
- `docx_analyzer`：生成 before/after 评分，包含 reference_check 和 figure_table_check。
- `reference_check`：检查参考文献章节、编号、跳号、重复编号、正文引用和未引用条目。
- `figure_table_check`：检查图题/表题编号、跳号、重复编号和正文引用不存在的图表编号。
- `agent_pipeline`：作为 API 和核心 Agent 之间的薄调度层，标准化返回字段和 trace，不重构核心逻辑。
- `agent_trace`：步骤级执行记录，解释处理链路、耗时、fallback 和每步 message。
- `task_state`：任务生命周期记录，默认写入 `paper-ai/backend/task_states/{task_id}.json`。
- local/ai fallback：local 模式不启用 AI 评分；ai 模式失败时 fallback，不让 AI 故障中断主流程。
- demo_outputs 四件套：`formatted_result_sample.docx`、`report_sample.json`、`agent_trace_sample.json`、`task_state_sample.json`。

## E. 项目亮点

- 不只是调模型，而是结构化 DOCX 文档处理 + Agent 调度 + 可解释报告。
- 支持模板规则提取，模板不完整时可以 fallback。
- 支持 before/after score，用 `80 -> 86` 展示格式处理效果。
- 支持结构化修改报告，说明改了什么、哪些还要人工复查。
- 支持 reference_check 和 figure_table_check，能解释参考文献和图表编号风险。
- 支持 agent_trace 可观测，前端 TracePanel 默认折叠展示。
- 支持 task_state 最小状态持久化，用于记录任务生命周期。
- 有真实可运行 demo 文件和固定 demo_outputs。
- 有 smoke、构建和 final demo check 记录。
- 前端已有产品化展示页，更适合现场讲解。
- v0.9.4 已整理截图/录屏清单，让面试展示材料更容易复用到 README、简历附件、作品集和 PPT。

## F. 截图/录屏素材建议

详细清单见 `docs/DEMO_SCREENSHOT_GUIDE.md`。

建议至少准备 13 张截图：首页 Hero、上传工作台、文件已选择、运行中状态、结果 dashboard、评分 `80 -> 86`、修改报告、参考文献/图表检查、TracePanel 默认折叠、TracePanel 展开 9 步、在线预览、下载入口和 390px 窄屏适配。

录屏建议控制在 60-90 秒：先展示页面定位，再上传 demo 论文和模板，选择本地规则模式，点击启动 Agent，展示评分、报告、检查结果、TracePanel、预览和下载。讲 TracePanel 时强调“Agent 可观测”，不要说成完整工业级调度平台。

自动化录屏建议使用 ASCII 临时路径，例如 `C:\Temp\paper-ai-demo\`，并在结束后确认 `git status --short` 干净、临时服务已停止。

## G. 当前边界

- 不是论文代写，不生成实验结果、观点或参考文献正文。
- 不是正式查重，只做重复风险检测 / 相似度预检。
- 不是完整工业级 Agent，没有用户系统、任务队列、多租户或云部署。
- 不是异步队列，`/agent/run` 仍是同步执行。
- 不是完整断点续跑，task_state 只是状态持久化雏形。
- 前端不读取 task_state 文件内容，只展示 `task_id` 和 `task_state_path` 摘要。
- AI 内容修改能力仍有限，当前主要是语言审校建议和参考评分。
- 复杂模板、目录、脚注、公式、页眉页脚和复杂图文排版仍可能需要人工复核。
- demo 样本是人工构造的脱敏模拟文本，不来自真实用户论文，也不来自 CAJ 原文。

## H. 面试追问回答

### 1. 为什么不用大模型直接改 Word？

Word 格式问题不是单纯文本生成问题。标题层级、行距、缩进、页边距、参考文献编号和图表引用都需要结构化 DOCX 解析和确定性规则。大模型可以做语言建议，但直接让它改 Word 容易不可控、不可测试，也难以保证下载文件格式稳定。

### 2. `agent_pipeline` 有什么作用？

它是 API 层和核心处理流程之间的薄包装层。它不重写 `paper_agent` 的核心逻辑，主要负责统一调用、补充 `agent_trace`、透出 `reference_check` / `figure_table_check`、写入 task_state，并保持旧字段兼容。

### 3. `agent_trace` 和 `task_state` 有什么区别？

`agent_trace` 记录步骤，回答“这次处理经历了什么”。`task_state` 记录生命周期，回答“这次任务是否 running/succeeded/failed，输入输出和总耗时是什么”。前者适合步骤解释，后者适合任务状态追踪；两者不互相替代。

### 4. AI 失败怎么办？

AI 是增强项，不是主流程唯一依赖。ai 模式下 LLM 调用失败会 fallback 到本地规则，主流程仍应返回结果、预览和下载。local 模式完全不依赖 AI。

### 5. 为什么 local 模式 `ai_score=null`、`ai_used=false`？

这是为了保证评分语义真实。local 模式没有调用 AI，就不应该展示 AI 分数或假装 AI 参与。这样面试时也能说明系统没有夸大能力。

### 6. 怎么证明修改有效？

可以从四层证明：before/after score 从 `80 -> 86`，`modification_report` 说明具体改动，reference_check / figure_table_check 展示可检查风险，最终 DOCX 可以预览和下载。

### 7. 如何避免运行产物污染 Git？

`.gitignore` 已忽略 `paper-ai/backend/task_states/` 和 `paper-ai/backend/templates/*.docx`。v0.9.2 final demo check 后 `git status --short` 仍干净，说明模板上传副本和 task_state 运行产物不会进入版本控制。

### 8. 当前项目最大不足是什么？

内容级修改仍弱。AI 模式主要做语言审校建议和参考评分，不是深度段落级润色，也不会补写事实或实验结论。复杂 Word 对象也需要继续增强。

### 9. 下一步怎么做？

短期整理截图/录屏清单，形成演示候选版本；中期做断点续跑设计；之后引入真实脱敏用户样本试用，继续增强复杂模板和内容级问题识别。

### 10. 如果要上线，还缺什么？

至少还需要用户系统、文件隔离、任务队列、任务清理策略、安全读取 task_state 的接口、权限控制、云部署、日志审计、异常告警、真实用户样本评估和隐私合规流程。

### 11. 前端产品化首页有什么意义？

它让面试官第一眼能看懂项目不是零散脚本，而是一个完整工具：首屏说明能力，工作台承接上传，结果区像 dashboard，TracePanel 解释 Agent 执行过程。

### 12. 为什么默认使用 `http://127.0.0.1:8000`？

本地 FastAPI 默认监听 HTTP 8000，统一使用 `127.0.0.1` 可以避免 `localhost` / `127.0.0.1` 或 `http` / `https` 混用。v0.9.2 也支持 `NEXT_PUBLIC_API_BASE_URL` 覆盖。

### 13. 为什么自动化上传建议使用 ASCII 临时路径？

在当前 Windows + CDP 自动化环境中，中文仓库路径下的文件句柄曾触发 `NotFoundError`，并在 Network 中表现为上传请求失败。把同内容文件复制到 ASCII 临时路径后，真实页面流程稳定通过。这是自动化环境兼容问题，不是 demo 文件来源变化。

### 14. `ERR_ALPN_NEGOTIATION_FAILED` 是怎么定位的？

先确认 Python 直调 `/agent/run` 返回 200，排除后端字段和业务错误；再用浏览器 Network 捕获到 `/document/classify` 和 `/agent/run` 的 loadingFailed；最后对比小请求、ASCII 临时路径和真实页面流程，定位为本地浏览器自动化上传路径兼容问题，并通过统一 API base URL 和更清晰错误提示降低排查成本。
