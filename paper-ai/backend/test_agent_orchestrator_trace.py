from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

import services.language_reviewer as language_reviewer
from services.paper_agent import run_paper_agent


def make_docx(path: Path, paragraphs: list[str]) -> None:
    document = Document()
    for text in paragraphs:
        document.add_paragraph(text)
    document.save(path)


def make_academic_docx(path: Path) -> None:
    make_docx(
        path,
        [
            "高中生压力管理研究",
            "摘要：本文围绕高中生压力管理展开分析。",
            "关键词：压力管理；高中生；教育研究",
            "1. 绪论",
            "当前高中生面对学业与生活压力。",
            "2. 研究方法",
            "本文采用文献分析方法。",
            "3. 结论",
            "本文认为需要从学校、家庭和学生自身三个方面改进压力管理。",
        ],
    )


def make_lab_report_docx(path: Path) -> None:
    make_docx(
        path,
        [
            "Linux 操作系统实验报告",
            "实验目的：掌握常用命令。",
            "实验内容：文件管理与进程查看。",
            "实验步骤：登录系统并执行命令。",
            "实验结果：命令输出符合预期。",
            "实验分析：系统调用结果正常。",
        ],
    )


def assert_ok(name: str, condition: bool, detail: object = "") -> None:
    if not condition:
        raise AssertionError(f"{name} FAIL {detail}")
    suffix = f" {detail}" if detail else ""
    print(f"{name} PASS{suffix}")


def assert_trace_shape(trace: dict[str, object]) -> None:
    required_keys = {
        "version",
        "task_plan",
        "tools_used",
        "agent_decision",
        "fallback_reason",
        "manual_review_required",
        "confidence",
    }
    assert_ok("trace_required_keys", required_keys.issubset(trace.keys()), trace.keys())
    task_ids = {item["id"] for item in trace["task_plan"]}
    assert_ok(
        "trace_task_plan_ids",
        {
            "classify_document",
            "analyze_before",
            "extract_template",
            "format_document",
            "language_review",
            "analyze_after",
            "generate_report",
        }.issubset(task_ids),
        task_ids,
    )


def main() -> None:
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        academic = tmp_path / "paper.docx"
        make_academic_docx(academic)

        local_result = run_paper_agent(academic, output_dir, mode="local")
        assert_ok("local_status_ok", local_result.get("status") == "ok", local_result.get("status"))
        assert_trace_shape(local_result["agent_trace"])
        assert_ok("local_trace_exists", bool(local_result.get("agent_trace")))
        assert_ok("local_mode_decision", local_result["agent_trace"]["agent_decision"]["mode"] == "local")
        assert_ok("local_fallback_reason", "local_mode_skip_ai" in local_result["agent_trace"]["fallback_reason"])
        assert_ok("manual_review_required_true", local_result["agent_trace"]["manual_review_required"] is True)
        for key in ["steps", "before_score", "after_score", "modification_report", "download_url"]:
            assert_ok(f"old_field_{key}", key in local_result)

        def fail_ai(_path: Path) -> dict[str, object]:
            raise RuntimeError("simulated ai failure")

        os.environ["DEEPSEEK_API_KEY"] = "fake-key"
        os.environ.pop("OPENAI_API_KEY", None)
        language_reviewer.call_ai_language_review = fail_ai
        ai_result = run_paper_agent(academic, output_dir, mode="ai")
        assert_ok("ai_fallback_status_ok", ai_result.get("status") == "ok", ai_result.get("status"))
        assert_ok(
            "ai_fallback_reason",
            "llm_unavailable_use_local_rules" in ai_result["agent_trace"]["fallback_reason"],
            ai_result["agent_trace"]["fallback_reason"],
        )

        lab_report = tmp_path / "lab_report.docx"
        make_lab_report_docx(lab_report)
        confirmation_result = run_paper_agent(lab_report, output_dir, mode="local", allow_non_paper=False)
        assert_ok("requires_confirmation_status", confirmation_result.get("status") == "requires_confirmation", confirmation_result)
        assert_trace_shape(confirmation_result["agent_trace"])
        assert_ok(
            "requires_confirmation_fallback",
            "non_paper_requires_confirmation" in confirmation_result["agent_trace"]["fallback_reason"],
            confirmation_result["agent_trace"]["fallback_reason"],
        )
        assert_ok("requires_confirmation_manual_review", confirmation_result["agent_trace"]["manual_review_required"] is True)

    print("AGENT_ORCHESTRATOR_TRACE PASS")


if __name__ == "__main__":
    main()
