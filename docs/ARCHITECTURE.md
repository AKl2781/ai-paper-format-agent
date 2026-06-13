# 系统架构说明

版本：`v0.6.1-demo-polish`

本文档说明 AI论文格式修改Agent 的现有架构。当前系统以 DOCX 论文格式处理为主，通过 FastAPI + Next.js 提供上传、预览和下载，通过后端工具链完成分类、格式修复、检查、评分和报告生成。

本文档只描述已经实现的内容，不包含未接入的 RAG、LangGraph、Milvus、数据库、用户系统或云部署。

## 总体架构

```mermaid
flowchart TD
    U["用户"] --> FE["Next.js 前端"]
    FE --> API["FastAPI main.py"]
    API --> PIPE["agent_pipeline.py 统一调度层"]
    PIPE --> AGENT["paper_agent.py 核心 Agent 流程"]

    AGENT --> CLF["document_classifier.py 文档分类"]
    AGENT --> RISK1["plagiarism_checker.py 修改前相似度预检"]
    AGENT --> ANL1["docx_analyzer.py 修改前分析"]
    AGENT --> TPL["template_extractor.py 模板解析"]
    AGENT --> FMT["docx_formatter.py 格式修复"]
    AGENT --> LANG["language_reviewer.py AI/本地语言审校"]
    AGENT --> RISK2["plagiarism_checker.py 修改后相似度预检"]
    AGENT --> ANL2["docx_analyzer.py 修改后分析"]
    AGENT --> RPT["build_modification_report 修改报告"]

    API --> PREVIEW["preview_service.py 在线预览"]
    API --> DOWNLOAD["/download/{filename} 下载 DOCX"]
    FMT --> OUT["outputs/*.docx"]
    LANG --> OUT
    PREVIEW --> OUT
    DOWNLOAD --> OUT
```

## 分层职责

### 前端层

位置：`paper-ai/frontend/`

- 负责上传论文和可选模板。
- 选择 `local` 或 `ai` 模式。
- 展示执行步骤、评分、修改报告、重复风险提示、参考文献检查、图表编号检查。
- 调用预览接口展示最终 DOCX 的 HTML 预览。
- 提供下载入口。

前端不直接解析或修改 DOCX。

### API 层

位置：`paper-ai/backend/main.py`

- `GET /health`：健康检查。
- `POST /document/classify`：上传 DOCX 并识别文档类型。
- `POST /agent/run`：保存上传文件，调用 `run_agent_pipeline(...)`。
- `GET /preview/{filename}`：读取输出 DOCX，生成 HTML 预览。
- `GET /download/{filename}`：下载输出 DOCX。

API 层不承载复杂业务规则，主要负责文件保存、路由和响应。

### 统一调度层

位置：`paper-ai/backend/services/agent_pipeline.py`

`agent_pipeline.py` 是 `/agent/run` 与核心 Agent 之间的薄调度层。它不重写核心业务流程，主要做三件事：

- 调用 `paper_agent.run_paper_agent(...)`。
- 将旧的解释型 trace 保留为 `agent_trace_detail`。
- 将展示用 `agent_trace` 标准化为逐步列表。

标准化后的 `agent_trace` 每项包含：

```json
{
  "step": "识别文档类型",
  "status": "ok",
  "duration_ms": 12,
  "fallback_used": false,
  "message": "文档类型：标准论文，置信度 95%。"
}
```

这个设计的目的不是引入复杂框架，而是让处理过程更容易在面试、调试和测试中解释。

### 核心 Agent 流程

位置：`paper-ai/backend/services/paper_agent.py`

核心流程顺序如下：

1. `classify_document(...)` 识别文档类型。
2. 如果是非标准论文且未确认，返回 `requires_confirmation`。
3. 修改前执行重复风险检测和格式分析。
4. 解析上传模板；没有模板时使用通用论文规则。
5. `apply_paper_format(...)` 修改 DOCX 格式。
6. `local` 模式跳过 AI；`ai` 模式尝试语言审校。
7. AI 调用失败时 fallback 到本地语言规则。
8. 修改后再次做重复风险检测和评分分析。
9. 构建 `modification_report`。
10. 返回结果、下载文件名、报告、trace 和兼容字段。

## agent_trace 与 agent_trace_detail

当前系统有两层 trace：

- `agent_trace`：展示版逐步列表，适合前端展示和面试说明。
- `agent_trace_detail`：旧解释型对象，保留任务计划、工具调用、Agent 决策、fallback 原因、人工复查判断和置信度。

这样做的原因：

- 新 trace 对面试展示更直观。
- 旧 trace 对调试和已有测试仍有价值。
- 不删除旧结构，降低兼容风险。

## local / ai 模式

### local 模式

local 模式只依赖本地规则：

- 执行文档分类。
- 执行格式修复。
- 执行重复风险检测 / 相似度预检。
- 执行参考文献和图表编号检查。
- 生成修改报告。
- 不启用 AI 语言评分。

必须满足：

- `ai_score = null`
- `ai_used = false`

### ai 模式

ai 模式在 local 格式修复基础上尝试语言审校：

- 如果 LLM 调用成功，返回 AI 语言参考评分和建议。
- 如果 LLM 调用失败，fallback 到本地语言规则。
- AI 语言评分只作参考，不参与主评分计算。
- AI 失败不应中断主流程。

## fallback 策略

```mermaid
flowchart TD
    A["开始处理"] --> B{"是否上传模板"}
    B -->|否| C["使用通用论文规则 fallback"]
    B -->|是| D["解析模板"]
    D --> E{"模板是否有 warning"}
    E -->|是| F["保留 warning，继续处理"]
    E -->|否| G["使用模板规则"]

    G --> H{"mode=ai"}
    F --> H
    C --> H
    H -->|否| I["local: 跳过 AI"]
    H -->|是| J["调用 LLM"]
    J --> K{"LLM 是否成功"}
    K -->|是| L["使用 AI 审校结果"]
    K -->|否| M["本地语言规则 fallback"]
    I --> N["继续评分和报告"]
    L --> N
    M --> N
```

已实现 fallback 场景：

- 未上传模板：通用论文规则。
- 模板解析 warning：记录 warning，继续处理。
- local 模式：明确跳过 AI。
- ai 模式 LLM 失败：本地规则 fallback。
- 重复风险检测异常：返回占位低风险结果，主流程继续。
- 非标准论文：返回 `requires_confirmation`，由用户确认后继续。

## 旧字段兼容

为了保持前端和测试稳定，结果中继续保留：

- `steps`
- `before_score`
- `after_score`
- `score_breakdown`
- `repeat_risk`
- `download_url`
- `filename`
- `before_analysis`
- `after_analysis`
- `modification_report`
- `language_review`
- `reference_check`
- `figure_table_check`

其中 `reference_check` 和 `figure_table_check` 既保留在 `after_analysis` 中，也同步到顶层，便于旧代码读取。

## 测试覆盖

现有测试重点覆盖：

- 参考文献检查：`test_reference_checker.py`
- 图表编号检查：`test_figure_table_checker.py`
- 风险等级：`test_risk_level_system.py`
- 复合编号：`test_composite_numbering.py`
- 标题正文混排：`test_formatter_mixed_heading.py`
- 评分语义和 AI 分数不拉低最终分：`test_score_consistency.py`
- 旧解释型 trace：`test_agent_orchestrator_trace.py`
- 上传处理主流程、模板、local、ai fallback、预览、下载、新 `agent_trace`：`test_smoke_agent_flow.py`

## 设计取舍

- 选择显式工具链，而不是让 LLM 自由决定处理流程。
- 选择薄调度层，而不是引入大型编排框架。
- 选择保留旧字段，而不是一次性调整前后端协议。
- 选择让 AI 失败 fallback，而不是把 AI 失败暴露为用户主流程失败。
- 选择明确产品边界：当前主要是格式 Agent，不夸大为深度内容改写 Agent。
