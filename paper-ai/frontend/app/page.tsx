"use client";

import { useMemo, useState } from "react";

type AgentStep = { name: string; status: "running" | "done" | "error"; message: string };
type AgentTraceItem = {
  step?: string;
  status?: string;
  duration_ms?: number;
  fallback_used?: boolean;
  message?: string;
};
type ScoreDimension = { key: string; label: string; score: number; group: "local" | "ai"; status: string; issues: string[] };
type Classification = {
  document_type: string;
  label: string;
  confidence: number;
  matched_features: string[];
  warning: string;
  requires_confirmation: boolean;
};
type ScoreBreakdown = {
  format_score?: number;
  risk_score?: number;
  ai_language_score?: number | null;
  local_score: number;
  ai_score: number | null;
  final_score: number;
  score_confidence?: number;
  score_explanation?: string;
  ai_used: boolean;
  ai_added_value: string[];
};
type ReferenceCheck = {
  has_reference_section: boolean;
  reference_count: number;
  citation_count: number;
  reference_numbers: number[];
  citation_numbers: number[];
  missing_reference_numbers: number[];
  uncited_reference_numbers: number[];
  duplicate_reference_numbers: number[];
  numbering_gaps: number[];
  issues: string[];
};
type FigureTableCheck = {
  figure_numbers: number[];
  table_numbers: number[];
  figure_gaps: number[];
  table_gaps: number[];
  duplicate_figures: number[];
  duplicate_tables: number[];
  missing_figure_captions: string[];
  missing_table_captions: string[];
  missing_referenced_figures: number[];
  missing_referenced_tables: number[];
  issues: string[];
};
type Analysis = {
  reference_check?: ReferenceCheck;
  figure_table_check?: FigureTableCheck;
  report: {
    score: number;
    summary: string;
    breakdown: ScoreDimension[];
    local_breakdown: ScoreDimension[];
    ai_breakdown: ScoreDimension[];
    score_breakdown: ScoreBreakdown;
    recommendations: string[];
  };
};
type RepeatRisk = { level: string; score: number; suggestions: string[] };
type ScoreComparison = { key: string; label: string; before: number; after: number; delta: number; status: string };
type FormatDiffSummary = {
  before_score: number;
  after_score: number;
  score_delta: number;
  auto_fix_count: number;
  changed_dimension_count: number;
  needs_manual_review_count: number;
  format_change_count: number;
  language_change_count: number;
  summary: string;
};
type ModificationReport = {
  summary: string;
  fixed_issues: string[];
  before_after: ScoreComparison[];
  format_diff_summary: FormatDiffSummary;
  changed_dimensions: ScoreComparison[];
  score_delta_by_dimension: Record<string, number>;
  auto_fix_count: number;
  needs_manual_review_count: number;
  change_counts: { format_changes: number; language_changes: number; total: number };
  unresolved_issues: string[];
  manual_review_items: string[];
  score_explanation?: string;
  template_used: string | null;
};
type AgentResult = {
  status: "ok" | "requires_confirmation";
  requires_confirmation: boolean;
  classification: Classification;
  steps: AgentStep[];
  before_score: number;
  after_score: number;
  score_breakdown: ScoreBreakdown;
  repeat_risk: RepeatRisk;
  download_url: string;
  filename: string;
  after_analysis: Analysis;
  modification_report: ModificationReport;
  agent_trace?: AgentTraceItem[];
  agent_trace_detail?: Record<string, unknown>;
  task_id?: string;
  task_state_path?: string;
};
type PreviewResult = { title: string; html: string };

const API_BASE = "http://127.0.0.1:8000";
const defaultSteps = ["识别文档类型", "读取论文", "分析本地格式", "识别模板格式", "修复标题样式", "AI增强审校", "重复风险预检", "最终复查", "生成最终报告"];

export default function Home() {
  const [paperFile, setPaperFile] = useState<File | null>(null);
  const [paperFilename, setPaperFilename] = useState("");
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [templateFilename, setTemplateFilename] = useState("");
  const [agentMode, setAgentMode] = useState<"local" | "ai">("ai");
  const [classification, setClassification] = useState<Classification | null>(null);
  const [confirmedNonPaper, setConfirmedNonPaper] = useState(false);
  const [result, setResult] = useState<AgentResult | null>(null);
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [previewError, setPreviewError] = useState("");
  const [message, setMessage] = useState("");
  const [running, setRunning] = useState(false);
  const [classifying, setClassifying] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);

  const visibleSteps = useMemo(() => {
    if (result?.steps.length) {
      const previewStep = preview ? [{ name: "生成在线预览", status: "done" as const, message: "已生成可在线查看的论文预览。" }] : [];
      return [...result.steps, ...previewStep];
    }
    return defaultSteps.map((name) => ({ name, status: "running" as const, message: "等待 Agent 调度" }));
  }, [result, preview]);

  const hasPaper = Boolean(paperFile);
  const needsConfirmation = classification?.requires_confirmation === true;
  const canRun = hasPaper && (!needsConfirmation || confirmedNonPaper);
  const buttonDisabled = running || !canRun;

  async function onPaperChange(file: File | null) {
    setPaperFile(file);
    setPaperFilename(file?.name ?? "");
    setClassification(null);
    setConfirmedNonPaper(false);
    setResult(null);
    setPreview(null);
    setPreviewError("");
    if (!file) {
      setMessage("");
      return;
    }
    await classifyFile(file);
  }

  function onTemplateChange(file: File | null) {
    setTemplateFile(file);
    setTemplateFilename(file?.name ?? "");
  }

  async function classifyFile(file: File) {
    const formData = new FormData();
    formData.append("paper", file);
    setClassifying(true);
    setMessage("正在识别文档类型...");
    try {
      const response = await fetch(`${API_BASE}/document/classify`, { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail ?? "文档类型识别失败。");
        return;
      }
      setClassification(data);
      setMessage(data.requires_confirmation ? "该文档可能不适合直接套用论文格式，请确认后继续。" : "已识别为标准论文，可以启动 Agent。");
    } catch {
      setMessage("文档类型识别失败。你仍可在确认文件无误后启动 Agent。");
    } finally {
      setClassifying(false);
    }
  }

  async function runAgent() {
    if (!paperFile) {
      setMessage("请先上传论文 docx 文件。");
      return;
    }
    if (needsConfirmation && !confirmedNonPaper) {
      setMessage("该文档可能不是标准论文，必须勾选确认后才能继续。");
      return;
    }

    const formData = new FormData();
    formData.append("paper", paperFile);
    formData.append("mode", agentMode);
    formData.append("allow_non_paper", String(Boolean(confirmedNonPaper)));
    if (templateFile) formData.append("template", templateFile);

    setRunning(true);
    setPreview(null);
    setPreviewError("");
    setResult(null);
    setMessage("论文修改 Agent 正在自主处理文档...");
    try {
      const response = await fetch(`${API_BASE}/agent/run`, { method: "POST", body: formData });
      const data = await response.json();
      if (data.status === "requires_confirmation") {
        setClassification(data.classification);
        setMessage(data.message);
        return;
      }
      if (!response.ok) {
        const detail = data.detail;
        setMessage(detail?.failed_step ? `Agent 在「${detail.failed_step}」失败：${detail.error}` : data.detail ?? "Agent 执行失败。");
        return;
      }
      setResult(data);
      setClassification(data.classification);
      setMessage("Agent 修改完成，正在生成在线预览。");
      const previewReady = await loadPreview(data.filename);
      setMessage(previewReady ? "Agent 修改完成，已生成修改报告和在线预览。" : "Agent 修改完成，修改报告和下载文件已生成，在线预览暂不可用。");
    } catch {
      setMessage("Agent 启动失败，请确认后端服务正在运行。");
    } finally {
      setRunning(false);
    }
  }

  async function loadPreview(filename: string): Promise<boolean> {
    setPreviewLoading(true);
    setPreviewError("");
    try {
      const response = await fetch(`${API_BASE}/preview/${encodeURIComponent(filename)}`);
      const data = await response.json();
      if (!response.ok) {
        const detail = data.detail ?? "在线预览生成失败。";
        setPreviewError(detail);
        setMessage(detail);
        return false;
      }
      setPreview(data);
      return true;
    } catch {
      const detail = "在线预览生成失败，请稍后重试。";
      setPreviewError(detail);
      setMessage(detail);
      return false;
    } finally {
      setPreviewLoading(false);
    }
  }

  return (
    <main className="page">
      <section className="workspace">
        <header className="hero">
          <p className="eyebrow">AI Paper Agent</p>
          <h1>AI论文格式修改Agent</h1>
          <p>上传论文后，Agent 会完成文档识别、格式修复、语言审校、重复风险预检、修改报告和在线预览。</p>
        </header>

        <section className="upload-grid" aria-label="上传文件">
          <FilePicker title="论文 docx" filename={paperFilename} onChange={onPaperChange} required />
          <FilePicker title="模板 docx" filename={templateFilename} onChange={onTemplateChange} />
        </section>

        <section className="mode-switch" aria-label="Agent 模式">
          <button className={agentMode === "local" ? "active" : ""} onClick={() => setAgentMode("local")} type="button">
            本地规则模式
            <span>只执行格式修复与重复风险预检</span>
          </button>
          <button className={agentMode === "ai" ? "active" : ""} onClick={() => setAgentMode("ai")} type="button">
            AI增强模式
            <span>增加语言、逻辑和学术表达评估</span>
          </button>
        </section>

        {classification ? <ClassificationCard classification={classification} confirmed={confirmedNonPaper} onConfirm={setConfirmedNonPaper} /> : null}

        <div className="action-row">
          <button className="agent-button" disabled={buttonDisabled} onClick={runAgent}>
            {running ? "Agent 执行中..." : result ? "重新运行Agent" : "启动论文修改 Agent"}
          </button>
          {result ? (
            <button className="secondary-button" disabled={previewLoading} onClick={() => loadPreview(result.filename)}>
              {previewLoading ? "生成预览中..." : "刷新在线预览"}
            </button>
          ) : null}
        </div>

        {message ? <p className={message.includes("失败") || message.includes("必须") ? "message error" : "message"}>{message}</p> : null}

        {(running || result) ? <ProgressPanel running={running} steps={visibleSteps} /> : null}

        {result?.download_url ? (
          <section className="result-panel" aria-label="Agent 结果">
            <div className="completion-strip">
              <span>Agent修改完成</span>
              <span>已生成修改报告</span>
              <span>{preview ? "已生成在线预览" : previewError ? "在线预览暂不可用" : "正在生成在线预览"}</span>
            </div>

            <ScoreOverview result={result} />
            <TracePanel result={result} />

            <section className="preview-panel">
              <div className="section-title">
                <span>在线预览</span>
                <strong>{preview?.title ?? (previewError ? "预览暂不可用" : "预览生成中")}</strong>
              </div>
              {previewLoading ? <div className="preview-status">正在生成修改后的论文预览...</div> : null}
              {previewError ? (
                <div className="preview-error">
                  <strong>在线预览生成失败</strong>
                  <span>{previewError}</span>
                </div>
              ) : null}
              {preview ? <article className="doc-preview" dangerouslySetInnerHTML={{ __html: preview.html }} /> : null}
              {!preview && !previewError ? <div className="preview-loading">正在生成修改后的论文预览...</div> : null}
            </section>

            <ScoreModules title="格式规则评分" items={result.after_analysis.report.local_breakdown} />
            {result.score_breakdown.ai_used ? <ScoreModules title="AI语言参考评分" items={result.after_analysis.report.ai_breakdown} /> : null}
            {result.after_analysis.reference_check ? <ReferenceCheckPanel check={result.after_analysis.reference_check} /> : null}
            {result.after_analysis.figure_table_check ? <FigureTableCheckPanel check={result.after_analysis.figure_table_check} /> : null}

            <section className="report-panel">
              <div className="section-title">
                <span>Agent修改报告</span>
                <strong>{result.modification_report.change_counts.total} 项处理</strong>
              </div>
              <p className="report-summary">{result.modification_report.summary}</p>
              <DiffReport report={result.modification_report} />
              {result.modification_report.score_explanation ? <p className="score-explanation">{result.modification_report.score_explanation}</p> : null}
              {result.score_breakdown.ai_added_value.length ? <ReportList title="AI语言参考说明" items={result.score_breakdown.ai_added_value} /> : null}
              <div className="report-grid">
                <ReportList title="已修复的问题" items={result.modification_report.fixed_issues} />
                <ReportList title="未能自动修复的问题" items={result.modification_report.unresolved_issues} />
              </div>
            </section>

            <section className="risk-box">
              <div className="section-title">
                <span>重复风险与人工复查</span>
                <strong>相似度预检 {result.repeat_risk.score}/100</strong>
              </div>
              <div className="report-grid">
                <ReportList title="降重建议" items={result.repeat_risk.suggestions} />
                <ReportList title="建议人工复查项" items={result.modification_report.manual_review_items} />
              </div>
            </section>

            <a className="download" href={`${API_BASE}${result.download_url}`} download>
              下载最终docx
            </a>
          </section>
        ) : null}
      </section>
    </main>
  );
}

function ClassificationCard({ classification, confirmed, onConfirm }: { classification: Classification; confirmed: boolean; onConfirm: (value: boolean) => void }) {
  return (
    <section className={classification.requires_confirmation ? "classification warning" : "classification"}>
      <div>
        <span>文档类型</span>
        <strong>{classification.label}</strong>
      </div>
      <div>
        <span>置信度</span>
        <strong>{Math.round(classification.confidence * 100)}%</strong>
      </div>
      <p>匹配特征：{classification.matched_features.length ? classification.matched_features.join("、") : "暂无明显特征"}</p>
      {classification.warning ? <p>{classification.warning}</p> : null}
      {classification.requires_confirmation ? (
        <label className="confirm-line">
          <input type="checkbox" checked={confirmed} onChange={(event) => onConfirm(event.target.checked)} />
          我确认继续按论文格式处理
        </label>
      ) : null}
    </section>
  );
}

function ProgressPanel({ running, steps }: { running: boolean; steps: AgentStep[] }) {
  return (
    <section className="agent-panel" aria-label="Agent 执行进度">
      <div className="section-title">
        <span>Agent执行过程</span>
        {running ? <strong>自主处理中</strong> : <strong>已完成</strong>}
      </div>
      <ol className="timeline">
        {steps.map((step) => (
          <li className={step.status} key={step.name}>
            <span className="step-icon">{step.status === "done" ? "✓" : step.status === "error" ? "!" : "•"}</span>
            <div>
              <strong>{step.name}</strong>
              <p>{step.message}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}

function TracePanel({ result }: { result: AgentResult }) {
  const traceItems = Array.isArray(result.agent_trace) ? result.agent_trace : [];
  const hasTaskStateSummary = Boolean(result.task_id || result.task_state_path);

  if (!traceItems.length && !hasTaskStateSummary) {
    return null;
  }

  return (
    <details className="trace-panel">
      <summary>
        <span>Agent Trace / 任务状态摘要</span>
        <strong>{traceItems.length ? `${traceItems.length} 个步骤` : "仅状态摘要"}</strong>
      </summary>

      <div className="trace-intro">
        <p>agent_trace 是步骤级执行记录；task_id 和 task_state_path 是后端本地任务状态摘要。</p>
        <p>当前仍是同步执行接口，不是异步队列，也不是完整断点续跑。前端不读取 task_state 文件内容。</p>
      </div>

      {hasTaskStateSummary ? (
        <div className="trace-state">
          {result.task_id ? (
            <div>
              <span>task_id</span>
              <code>{result.task_id}</code>
            </div>
          ) : null}
          {result.task_state_path ? (
            <div>
              <span>task_state_path</span>
              <code>{result.task_state_path}</code>
            </div>
          ) : null}
          <p>task_state_path 为后端本地运行产物路径，仅用于开发/演示排查。</p>
        </div>
      ) : null}

      {traceItems.length ? (
        <ol className="trace-list">
          {traceItems.map((item, index) => (
            <li className={traceStatusTone(item.status)} key={`${item.step ?? "trace"}-${index}`}>
              <div className="trace-item-head">
                <strong>{item.step || `step_${index + 1}`}</strong>
                <span>{traceStatusLabel(item.status)}</span>
              </div>
              {item.message ? <p>{item.message}</p> : null}
              <div className="trace-meta">
                <span>{formatTraceDuration(item.duration_ms)}</span>
                <span>{item.fallback_used ? "已使用 fallback / 本地规则" : "未标记 fallback"}</span>
              </div>
            </li>
          ))}
        </ol>
      ) : null}
    </details>
  );
}

function ScoreOverview({ result }: { result: AgentResult }) {
  const formatScore = result.score_breakdown.format_score ?? result.score_breakdown.local_score;
  const aiLanguageScore = result.score_breakdown.ai_language_score ?? result.score_breakdown.ai_score;
  const aiIsReferenceOnly = typeof aiLanguageScore === "number" && aiLanguageScore < formatScore;

  return (
    <div className="score-overview">
      <div>
        <span>最终评分</span>
        <strong>{result.score_breakdown.final_score}</strong>
        <p>{result.after_analysis.report.summary}</p>
      </div>
      <div className="score-change">
        <span>格式规则分</span>
        <b>{formatScore}</b>
        <span>风险稳定分</span>
        <b>{result.score_breakdown.risk_score ?? "待评估"}</b>
        <span>AI语言参考分</span>
        <b>{aiLanguageScore ?? "未启用"}</b>
        <small>可信度 {result.score_breakdown.score_confidence ?? "待评估"}</small>
        {aiIsReferenceOnly ? <p className="score-note">AI语言评分仅作参考，不影响最终评分。</p> : null}
      </div>
      <div className={`risk-pill ${riskTone(result.repeat_risk.level)}`}>
        <span>重复风险</span>
        <strong>{result.repeat_risk.level}</strong>
        <small>{result.repeat_risk.score}/100</small>
      </div>
    </div>
  );
}

function ScoreModules({ title, items }: { title: string; items: ScoreDimension[] }) {
  return (
    <section className="module-panel">
      <div className="section-title">
        <span>{title}</span>
        <strong>{items.length} 项</strong>
      </div>
      <div className="module-grid">
        {items.map((item) => (
          <ScoreModule key={item.key} item={item} />
        ))}
      </div>
    </section>
  );
}

function FilePicker({ title, filename, required = false, onChange }: { title: string; filename: string; required?: boolean; onChange: (file: File | null) => void }) {
  return (
    <label className="file-card">
      <span>
        {title}
        <b>{required ? "必选" : "可选"}</b>
      </span>
      <strong>{filename || "选择 Word 文件"}</strong>
      <input accept=".docx" type="file" onChange={(event) => onChange(event.target.files?.[0] ?? null)} />
    </label>
  );
}

function ScoreModule({ item }: { item: ScoreDimension }) {
  return (
    <div className="module-card">
      <div>
        <span>{item.label}</span>
        <strong>{item.score}</strong>
      </div>
      <div className="bar">
        <i style={{ width: `${item.score}%` }} />
      </div>
      <p>{item.status}</p>
      {item.issues.length ? <small>{item.issues[0]}</small> : <small>自动检查未发现明显风险。</small>}
    </div>
  );
}

function ReportList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="report-list">
      <h2>{title}</h2>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function ReferenceCheckPanel({ check }: { check: ReferenceCheck }) {
  const summaryItems = [
    `参考文献章节：${check.has_reference_section ? "已识别" : "未识别"}`,
    `文末条目：${check.reference_count} 条`,
    `正文引用：${check.citation_count} 处`,
  ];
  const relationItems = [
    `文末编号：${formatNumbers(check.reference_numbers)}`,
    `正文引用编号：${formatNumbers(check.citation_numbers)}`,
    `跳号：${formatNumbers(check.numbering_gaps)}`,
    `重复编号：${formatNumbers(check.duplicate_reference_numbers)}`,
    `正文引用不存在：${formatNumbers(check.missing_reference_numbers)}`,
    `文末未引用：${formatNumbers(check.uncited_reference_numbers)}`,
  ];
  const issueItems = check.issues.length ? check.issues : ["自动检查未发现明显参考文献风险。"];
  return (
    <section className="module-panel">
      <div className="section-title">
        <span>参考文献检查</span>
        <strong>{check.reference_count} 条文献</strong>
      </div>
      <div className="report-grid">
        <ReportList title="检查概览" items={summaryItems} />
        <ReportList title="编号与引用" items={relationItems} />
      </div>
      <ReportList title="参考文献风险" items={issueItems} />
    </section>
  );
}

function FigureTableCheckPanel({ check }: { check: FigureTableCheck }) {
  const summaryItems = [
    `图题编号：${formatNumbers(check.figure_numbers)}`,
    `表题编号：${formatNumbers(check.table_numbers)}`,
    `图编号跳号：${formatNumbers(check.figure_gaps)}`,
    `表编号跳号：${formatNumbers(check.table_gaps)}`,
  ];
  const riskItems = [
    `重复图编号：${formatNumbers(check.duplicate_figures)}`,
    `重复表编号：${formatNumbers(check.duplicate_tables)}`,
    `正文引用图号不存在：${formatNumbers(check.missing_referenced_figures)}`,
    `正文引用表号不存在：${formatNumbers(check.missing_referenced_tables)}`,
  ];
  const captionItems = [...check.missing_figure_captions, ...check.missing_table_captions];
  const issueItems = check.issues.length ? check.issues : ["自动检查未发现明显图表编号风险。"];
  return (
    <section className="module-panel">
      <div className="section-title">
        <span>图表编号检查</span>
        <strong>{check.figure_numbers.length} 图 / {check.table_numbers.length} 表</strong>
      </div>
      <div className="report-grid">
        <ReportList title="编号概览" items={summaryItems} />
        <ReportList title="引用与重复" items={riskItems} />
      </div>
      {captionItems.length ? <ReportList title="题注缺失风险" items={captionItems} /> : null}
      <ReportList title="图表风险" items={issueItems} />
    </section>
  );
}

function DiffReport({ report }: { report: ModificationReport }) {
  const changedItems = report.changed_dimensions.length
    ? report.changed_dimensions.map((item) => `${item.label}：${item.before} → ${item.after}（${formatDelta(item.delta)}）`)
    : ["各评分维度保持稳定，本次主要完成格式规范化处理。"];
  return (
    <div className="diff-report">
      <div className="diff-summary">
        <div>
          <span>自动处理</span>
          <strong>{report.auto_fix_count}</strong>
        </div>
        <div>
          <span>变化维度</span>
          <strong>{report.format_diff_summary.changed_dimension_count}</strong>
        </div>
        <div>
          <span>人工复查</span>
          <strong>{report.needs_manual_review_count}</strong>
        </div>
      </div>
      <p>{report.format_diff_summary.summary}</p>
      <div className="report-grid">
        <ReportList title="改了什么" items={changedItems} />
        <ReportList title="仍需人工复查" items={report.manual_review_items} />
      </div>
    </div>
  );
}

function formatNumbers(numbers: number[]) {
  return numbers.length ? numbers.join("、") : "无";
}

function formatDelta(delta: number) {
  if (delta > 0) return `+${delta}`;
  return String(delta);
}

function formatTraceDuration(duration?: number) {
  return typeof duration === "number" ? `${duration} ms` : "未记录耗时";
}

function traceStatusLabel(status?: string) {
  if (!status) return "unknown";
  if (status === "done" || status === "ok" || status === "succeeded") return "done";
  if (status === "error" || status === "failed") return "error";
  if (status === "running") return "running";
  return status;
}

function traceStatusTone(status?: string) {
  const normalized = traceStatusLabel(status);
  if (normalized === "done") return "done";
  if (normalized === "error") return "error";
  if (normalized === "running") return "running";
  return "neutral";
}

function riskTone(level: string) {
  if (level === "高") return "risk-high";
  if (level === "中") return "risk-medium";
  return "risk-low";
}
