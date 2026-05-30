"use client";

import { useMemo, useState } from "react";

type AgentStep = { name: string; status: "running" | "done" | "error"; message: string };
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
  local_score: number;
  ai_score: number | null;
  final_score: number;
  ai_used: boolean;
  ai_added_value: string[];
};
type Analysis = {
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
type ModificationReport = {
  summary: string;
  fixed_issues: string[];
  before_after: Array<{ key: string; label: string; before: number; after: number; delta: number; status: string }>;
  change_counts: { format_changes: number; language_changes: number; total: number };
  unresolved_issues: string[];
  manual_review_items: string[];
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
      await loadPreview(data.filename);
      setMessage("Agent 修改完成，已生成修改报告和在线预览。");
    } catch {
      setMessage("Agent 启动失败，请确认后端服务正在运行。");
    } finally {
      setRunning(false);
    }
  }

  async function loadPreview(filename: string) {
    setPreviewLoading(true);
    try {
      const response = await fetch(`${API_BASE}/preview/${encodeURIComponent(filename)}`);
      const data = await response.json();
      if (!response.ok) {
        setMessage(data.detail ?? "在线预览生成失败。");
        return;
      }
      setPreview(data);
    } catch {
      setMessage("在线预览生成失败，请稍后重试。");
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
              <span>{preview ? "已生成在线预览" : "正在生成在线预览"}</span>
            </div>

            <ScoreOverview result={result} />

            <section className="preview-panel">
              <div className="section-title">
                <span>在线预览</span>
                <strong>{preview?.title ?? "预览生成中"}</strong>
              </div>
              {preview ? <article className="doc-preview" dangerouslySetInnerHTML={{ __html: preview.html }} /> : <div className="preview-loading">正在生成修改后的论文预览...</div>}
            </section>

            <ScoreModules title="本地规则评分" items={result.after_analysis.report.local_breakdown} />
            {result.score_breakdown.ai_used ? <ScoreModules title="AI增强评分" items={result.after_analysis.report.ai_breakdown} /> : null}

            <section className="report-panel">
              <div className="section-title">
                <span>Agent修改报告</span>
                <strong>{result.modification_report.change_counts.total} 项处理</strong>
              </div>
              <p className="report-summary">{result.modification_report.summary}</p>
              {result.score_breakdown.ai_added_value.length ? <ReportList title="AI额外提升" items={result.score_breakdown.ai_added_value} /> : null}
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

function ScoreOverview({ result }: { result: AgentResult }) {
  return (
    <div className="score-overview">
      <div>
        <span>最终评分</span>
        <strong>{result.score_breakdown.final_score}</strong>
        <p>{result.after_analysis.report.summary}</p>
      </div>
      <div className="score-change">
        <span>本地规则</span>
        <b>{result.score_breakdown.local_score}</b>
        <span>AI增强</span>
        <b>{result.score_breakdown.ai_score ?? "未启用"}</b>
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

function riskTone(level: string) {
  if (level === "高") return "risk-high";
  if (level === "中") return "risk-medium";
  return "risk-low";
}
