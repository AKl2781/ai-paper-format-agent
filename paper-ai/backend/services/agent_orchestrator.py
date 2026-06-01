from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


AGENT_TRACE_VERSION = "v0.3.7"
REVIEW_RISK_LEVELS = {"blocking", "high_risk"}


TASKS = [
    ("classify_document", "识别文档类型", "document_classifier.classify_document", True),
    ("analyze_before", "修改前分析", "docx_analyzer.analyze_docx", True),
    ("extract_template", "模板解析", "template_extractor.extract_template_profile", False),
    ("format_document", "格式修复", "docx_formatter.apply_paper_format", True),
    ("language_review", "语言审校", "language_reviewer.review_language_with_status", False),
    ("analyze_after", "修改后分析", "docx_analyzer.analyze_docx", True),
    ("generate_report", "生成报告", "report_generator/build_modification_report", True),
]


@dataclass
class AgentTraceBuilder:
    mode: str
    has_template: bool
    task_plan: list[dict[str, Any]] = field(default_factory=list)
    tools_used: list[dict[str, Any]] = field(default_factory=list)
    fallback_reasons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.task_plan = [
            {"id": task_id, "label": label, "tool": tool, "required": required, "status": "pending"}
            for task_id, label, tool, required in TASKS
        ]
        if not self.has_template:
            self.add_fallback("no_template_uploaded")

    def mark_task(self, task_id: str, status: str, summary: str | None = None) -> None:
        for task in self.task_plan:
            if task["id"] == task_id:
                task["status"] = status
                if summary:
                    task["summary"] = summary
                return

    def record_tool(self, name: str, status: str = "success", summary: str | None = None) -> None:
        item = {"name": name, "status": status}
        if summary:
            item["summary"] = summary
        self.tools_used.append(item)

    def add_fallback(self, reason: str | None) -> None:
        if reason and reason not in self.fallback_reasons:
            self.fallback_reasons.append(reason)

    def build(
        self,
        *,
        classification: dict[str, Any] | None = None,
        template_profile: dict[str, Any] | None = None,
        language_review: dict[str, Any] | None = None,
        modification_report: dict[str, Any] | None = None,
        after_analysis: dict[str, Any] | None = None,
        requires_confirmation: bool = False,
        status: str = "ok",
    ) -> dict[str, Any]:
        self._fill_pending_tasks(status)
        self._collect_fallbacks(template_profile, language_review, requires_confirmation)
        manual_review_required = needs_manual_review(modification_report, after_analysis, requires_confirmation)
        advisory_notice_required = has_advisory_notice(modification_report, after_analysis)
        return {
            "version": AGENT_TRACE_VERSION,
            "task_plan": self.task_plan,
            "tools_used": self.tools_used,
            "agent_decision": build_agent_decision(
                mode=self.mode,
                classification=classification,
                has_template=self.has_template,
                template_profile=template_profile,
                language_review=language_review,
                manual_review_required=manual_review_required,
                advisory_notice_required=advisory_notice_required,
                requires_confirmation=requires_confirmation,
            ),
            "fallback_reason": self.fallback_reasons,
            "manual_review_required": manual_review_required,
            "confidence": calculate_confidence(
                classification=classification,
                status=status,
                fallback_reasons=self.fallback_reasons,
                manual_review_required=manual_review_required,
                modification_report=modification_report,
                requires_confirmation=requires_confirmation,
            ),
        }

    def _collect_fallbacks(
        self,
        template_profile: dict[str, Any] | None,
        language_review: dict[str, Any] | None,
        requires_confirmation: bool,
    ) -> None:
        if template_profile and template_profile.get("warnings"):
            self.add_fallback("template_parse_warning")
        if self.mode == "local":
            self.add_fallback("local_mode_skip_ai")
        if self.mode == "ai" and language_review and language_review.get("mode") != "ai":
            self.add_fallback("llm_unavailable_use_local_rules")
        if requires_confirmation:
            self.add_fallback("non_paper_requires_confirmation")

    def _fill_pending_tasks(self, status: str) -> None:
        for task in self.task_plan:
            if task["status"] == "pending":
                task["status"] = "skipped" if status != "error" else "not_run"


def build_agent_decision(
    *,
    mode: str,
    classification: dict[str, Any] | None,
    has_template: bool,
    template_profile: dict[str, Any] | None,
    language_review: dict[str, Any] | None,
    manual_review_required: bool,
    advisory_notice_required: bool,
    requires_confirmation: bool,
) -> dict[str, Any]:
    document_type = (classification or {}).get("document_type")
    template_warnings = bool(template_profile and template_profile.get("warnings"))
    return {
        "mode": mode,
        "document_type": document_type,
        "template_strategy": template_strategy(has_template, template_warnings),
        "format_strategy": "apply_paper_format",
        "language_strategy": language_strategy(mode, language_review),
        "review_strategy": review_strategy(manual_review_required, advisory_notice_required, requires_confirmation),
    }


def template_strategy(has_template: bool, has_warnings: bool) -> str:
    if not has_template:
        return "default_rules"
    if has_warnings:
        return "template_with_fallback_warnings"
    return "uploaded_template"


def language_strategy(mode: str, language_review: dict[str, Any] | None) -> str:
    if mode == "local":
        return "skip_ai_review"
    if language_review and language_review.get("mode") == "ai":
        return "ai_review"
    return "local_language_fallback"


def review_strategy(manual_review_required: bool, advisory_notice_required: bool, requires_confirmation: bool) -> str:
    if requires_confirmation:
        return "user_confirmation_required"
    if manual_review_required:
        return "manual_review_recommended"
    if advisory_notice_required:
        return "advisory_notice_only"
    return "automatic_review_passed"


def needs_manual_review(
    modification_report: dict[str, Any] | None,
    after_analysis: dict[str, Any] | None,
    requires_confirmation: bool,
) -> bool:
    if requires_confirmation:
        return True
    if modification_report and modification_report.get("manual_review_items"):
        return True
    if after_analysis:
        if has_review_risk(after_analysis):
            return True
    return False


def has_review_risk(after_analysis: dict[str, Any]) -> bool:
    return any(item.get("level") in REVIEW_RISK_LEVELS for item in collect_check_risk_items(after_analysis))


def has_advisory_notice(
    modification_report: dict[str, Any] | None,
    after_analysis: dict[str, Any] | None,
) -> bool:
    if modification_report and (modification_report.get("warning_items") or modification_report.get("info_items")):
        return True
    if not after_analysis:
        return False
    return any(item.get("level") in {"warning", "info"} for item in collect_check_risk_items(after_analysis))


def collect_check_risk_items(after_analysis: dict[str, Any]) -> list[dict[str, Any]]:
    reference_items = (after_analysis.get("reference_check") or {}).get("risk_items") or []
    figure_table_items = (after_analysis.get("figure_table_check") or {}).get("risk_items") or []
    return [*reference_items, *figure_table_items]


def calculate_confidence(
    *,
    classification: dict[str, Any] | None,
    status: str,
    fallback_reasons: list[str],
    manual_review_required: bool,
    modification_report: dict[str, Any] | None,
    requires_confirmation: bool,
) -> float:
    try:
        score = float((classification or {}).get("confidence", 0.5))
    except (TypeError, ValueError):
        score = 0.5

    if status != "ok":
        score -= 0.18
    if requires_confirmation:
        score -= 0.12
    if manual_review_required:
        score -= 0.08
    if "template_parse_warning" in fallback_reasons:
        score -= 0.05
    if "llm_unavailable_use_local_rules" in fallback_reasons:
        score -= 0.06
    if modification_report:
        score += 0.05

    return round(max(0.1, min(0.98, score)), 2)
