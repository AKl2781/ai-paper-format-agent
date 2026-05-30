from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .document_classifier import classify_document
from .docx_analyzer import analyze_docx
from .docx_formatter import apply_paper_format
from .language_reviewer import apply_language_suggestions, review_language_with_status
from .plagiarism_checker import check_repeat_risk
from .template_extractor import extract_template_profile


@dataclass
class AgentState:
    paper_path: Path
    output_dir: Path
    template_path: Path | None = None
    steps: list[dict[str, str]] = field(default_factory=list)
    current_step: str = ""

    def start(self, name: str, message: str) -> None:
        self.current_step = name
        self.steps.append({"name": name, "status": "running", "message": message})

    def finish(self, message: str) -> None:
        self.steps[-1] = {"name": self.current_step, "status": "done", "message": message}

    def fail(self, message: str) -> None:
        if self.steps and self.steps[-1]["status"] == "running":
            self.steps[-1] = {"name": self.current_step, "status": "error", "message": message}
        else:
            self.steps.append({"name": self.current_step or "未知步骤", "status": "error", "message": message})


def run_paper_agent(
    paper_path: Path,
    output_dir: Path,
    template_path: Path | None = None,
    allow_non_paper: bool = False,
    mode: str = "ai",
) -> dict[str, Any]:
    state = AgentState(paper_path=paper_path, template_path=template_path, output_dir=output_dir)
    normalized_mode = "local" if mode == "local" else "ai"

    try:
        state.start("识别文档类型", "正在判断该文件是否为标准论文。")
        classification = classify_document(paper_path)
        if classification["requires_confirmation"] and not allow_non_paper:
            state.finish(classification["warning"])
            return {
                "status": "requires_confirmation",
                "requires_confirmation": True,
                "classification": classification,
                "steps": state.steps,
                "message": classification["warning"],
            }
        state.finish(f"文档类型：{classification['label']}，置信度 {round(classification['confidence'] * 100)}%。")

        state.start("读取论文", "正在读取 Word 文档、正文段落和基础样式。")
        if not paper_path.exists():
            raise FileNotFoundError("论文文件不存在")
        state.finish(f"已读取 {paper_path.name}")

        state.start("分析本地格式", "正在进行结构、标题、字体、行距、页边距和参考文献基础评估。")
        before_repeat = check_repeat_risk(paper_path)
        before_analysis = analyze_docx(paper_path, template_path=template_path, repeat_score=before_repeat["score_for_quality"])
        before_score = int(before_analysis["report"]["score"])
        state.finish(f"本地模式初评 {before_score}。")

        state.start("识别模板格式", "正在读取模板页边距、正文样式和标题格式。")
        template_profile = extract_template_profile(template_path) if template_path else None
        if template_profile and template_path:
            warnings = template_profile.get("warnings") or []
            warning_text = f"；提示：{'；'.join(warnings)}" if warnings else ""
            state.finish(f"已识别模板：{template_path.name}{warning_text}")
        else:
            state.finish("未上传模板，按通用论文规范执行。")

        state.start("修复标题与正文格式", "正在统一标题层级、正文字体、段落缩进和页面基础格式。")
        formatted_path = build_output_path(output_dir, paper_path, "formatted")
        format_log = apply_paper_format(paper_path, formatted_path, template_path)
        state.finish("标题、正文和页面基础格式已统一。")

        language_log: list[str] = []
        language_review: dict[str, Any] = {
            "mode": "local",
            "error": None,
            "suggestions": [],
            "ai_scores": None,
            "ai_added_value": [],
        }
        final_path = formatted_path

        if normalized_mode == "ai":
            state.start("AI增强审校", "正在分析语言规范性、表达流畅度、论文逻辑性和学术表达质量。")
            language_path = build_output_path(output_dir, paper_path, "language")
            language_review = review_language_with_status(formatted_path)
            suggestions = language_review["suggestions"]
            language_log = apply_language_suggestions(formatted_path, language_path, suggestions)
            final_path = language_path
            applied_language_count = len([item for item in language_log if "->" in item])
            if language_review["mode"] == "ai":
                warning = f"；提示：{language_review['error']}" if language_review.get("error") else ""
                state.finish(f"AI增强完成，应用 {applied_language_count} 条语言优化{warning}。")
            else:
                state.finish(f"AI不可用，已使用本地语言规则，应用 {applied_language_count} 条优化；提示：{language_review.get('error') or 'AI未返回可用结果'}。")
        else:
            state.start("AI增强审校", "本地规则模式已启用，本轮跳过 AI 语言审校。")
            state.finish("本地规则模式不计算 AI 语言、流畅度、逻辑和学术表达评分。")

        state.start("重复风险预检", "正在检测相似段落、重复句子和重复风险等级。")
        repeat_risk = check_repeat_risk(final_path)
        state.finish(f"重复风险等级：{repeat_risk['level']}，风险值 {repeat_risk['score']}/100。")

        state.start("最终复查", "正在计算本地评分、AI增强评分和最终评分。")
        after_analysis = analyze_docx(
            final_path,
            template_path=template_path,
            repeat_score=repeat_risk["score_for_quality"],
            ai_scores=language_review["ai_scores"] if normalized_mode == "ai" else None,
        )
        after_score = int(after_analysis["report"]["score"])
        score_breakdown = after_analysis["report"]["score_breakdown"]
        state.finish(f"最终评分 {after_score}，AI使用状态：{'已启用' if score_breakdown['ai_used'] else '未启用'}。")

        state.start("生成最终报告", "正在整理修复记录、前后对比和人工复查建议。")
        modification_report = build_modification_report(
            before_analysis,
            after_analysis,
            format_log,
            language_log,
            repeat_risk,
            template_path,
        )
        state.finish(f"报告已生成，最终文件：{final_path.name}")

        return {
            "status": "ok",
            "mode": normalized_mode,
            "requires_confirmation": False,
            "classification": classification,
            "steps": state.steps,
            "before_score": before_score,
            "after_score": after_score,
            "score_breakdown": score_breakdown,
            "repeat_risk": repeat_risk,
            "download_url": f"/download/{final_path.name}",
            "filename": final_path.name,
            "before_analysis": before_analysis,
            "after_analysis": after_analysis,
            "modification_report": modification_report,
            "language_review": {"mode": language_review["mode"], "error": language_review["error"]},
            "language_suggestions": language_review["suggestions"],
        }
    except Exception as exc:
        state.fail(str(exc))
        return {"status": "error", "failed_step": state.current_step, "steps": state.steps, "error": str(exc), "download_url": None}


def build_output_path(output_dir: Path, source: Path, suffix: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return output_dir / f"{source.stem}_{suffix}_{timestamp}.docx"


def build_modification_report(
    before_analysis: dict[str, Any],
    after_analysis: dict[str, Any],
    format_log: list[str],
    language_log: list[str],
    repeat_risk: dict[str, Any],
    template_path: Path | None,
) -> dict[str, Any]:
    before_items = {item["key"]: item for item in before_analysis["report"]["breakdown"]}
    comparisons = []
    for after_item in after_analysis["report"]["breakdown"]:
        before_item = before_items.get(after_item["key"], after_item)
        comparisons.append(
            {
                "key": after_item["key"],
                "label": after_item["label"],
                "before": before_item["score"],
                "after": after_item["score"],
                "delta": after_item["score"] - before_item["score"],
                "status": after_item["status"],
            }
        )

    language_changes = len([item for item in language_log if "->" in item])
    return {
        "summary": f"Agent 完成 {len(format_log) + language_changes} 项自动处理，最终评分 {after_analysis['report']['score']}。",
        "fixed_issues": [
            "统一页面边距、正文样式、标题层级和段落间距。",
            "完成本地格式修复和重复风险预检。",
            "根据当前模式完成语言审校或跳过 AI 增强。",
        ],
        "before_after": comparisons,
        "change_counts": {
            "format_changes": len(format_log),
            "language_changes": language_changes,
            "total": len(format_log) + language_changes,
        },
        "unresolved_issues": collect_unresolved(after_analysis),
        "manual_review_items": list(dict.fromkeys(after_analysis["report"]["recommendations"] + repeat_risk.get("suggestions", []))),
        "template_used": template_path.name if template_path else None,
    }


def collect_unresolved(after_analysis: dict[str, Any]) -> list[str]:
    issues = []
    for item in after_analysis["report"]["breakdown"]:
        if item["score"] < 90:
            item_issues = item["issues"] or ["仍建议人工复核。"]
            issues.extend([f"{item['label']}：{issue}" for issue in item_issues])
    return issues or ["未发现高风险未修复项，但最终提交前仍建议人工复查。"]
