from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory

from docx import Document

import services.language_reviewer as language_reviewer
from services.docx_analyzer import AI_WEIGHTS, LOCAL_WEIGHTS, build_score_breakdown
from services.paper_agent import run_paper_agent


def make_docx(path: Path) -> None:
    document = Document()
    for text in [
        "高中生压力管理研究",
        "摘要：本文围绕高中生压力管理展开分析，探讨学校支持与个人调适。",
        "关键词：压力管理；高中生；教育研究",
        "1. 绪论",
        "已有研究指出，压力管理需要学校、家庭和学生共同参与[1]。",
        "2. 研究方法",
        "本文采用文献分析方法，对高中生压力来源和应对方式进行归纳。",
        "3. 实验结果",
        "分析发现，清晰的时间规划和同伴支持有助于降低学习压力。",
        "4. 结论",
        "本文认为需要从学校、家庭和学生自身三个方面改进压力管理。",
        "参考文献",
        "[1] 张三. 高中生压力管理研究[J]. 教育研究, 2024.",
    ]:
        document.add_paragraph(text)
    document.save(path)


def score_items(keys: dict[str, float], score: int, group: str) -> list[dict[str, object]]:
    return [{"key": key, "label": key, "score": score, "status": "ok", "issues": [], "group": group} for key in keys]


def fake_ai_success(_path: Path) -> dict[str, object]:
    return {
        "suggestions": [],
        "ai_scores": {
            "language": 70,
            "fluency": 70,
            "logic": 70,
            "academic_expression": 70,
        },
        "ai_added_value": ["AI语言评分仅用于参考。"],
        "warning": None,
    }


def fake_ai_failure(_path: Path) -> dict[str, object]:
    raise RuntimeError("simulated ai failure")


def assert_ok(name: str, condition: bool, detail: object = "") -> None:
    if not condition:
        raise AssertionError(f"{name} FAIL {detail}")
    suffix = f" {detail}" if detail else ""
    print(f"{name} PASS{suffix}")


def assert_old_fields_compatible(result: dict[str, object]) -> None:
    for key in ["before_score", "after_score", "score_breakdown", "modification_report", "download_url"]:
        assert_ok(f"old_field_{key}", key in result)
    score_breakdown = result["score_breakdown"]
    assert_ok("old_score_local_score", "local_score" in score_breakdown)
    assert_ok("old_score_ai_score", "ai_score" in score_breakdown)
    assert_ok("old_score_ai_used", "ai_used" in score_breakdown)


def main() -> None:
    original_ai_call = language_reviewer.call_ai_language_review
    try:
        low_ai = build_score_breakdown(
            score_items(LOCAL_WEIGHTS, 88, "local"),
            score_items(AI_WEIGHTS, 70, "ai"),
            risk_score=96,
            risk_items=[],
        )
        assert_ok("direct_ai_language_score_lower", low_ai["ai_language_score"] < low_ai["format_score"], low_ai)
        assert_ok("direct_final_not_lowered_by_ai", low_ai["final_score"] == low_ai["format_score"], low_ai)
        assert_ok("direct_old_ai_score_alias", low_ai["ai_score"] == low_ai["ai_language_score"], low_ai)

        with TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            output_dir = tmp_path / "outputs"
            output_dir.mkdir()
            paper = tmp_path / "paper.docx"
            make_docx(paper)

            os.environ.pop("DEEPSEEK_API_KEY", None)
            os.environ.pop("OPENAI_API_KEY", None)
            local_result = run_paper_agent(paper, output_dir, mode="local")
            local_score = local_result["score_breakdown"]
            assert_ok("local_status_ok", local_result.get("status") == "ok", local_result.get("status"))
            assert_ok("local_ai_score_null", local_score["ai_score"] is None, local_score)
            assert_ok("local_ai_language_score_null", local_score["ai_language_score"] is None, local_score)
            assert_ok("local_ai_used_false", local_score["ai_used"] is False, local_score)
            assert_ok("local_final_is_format_score", local_score["final_score"] == local_score["format_score"], local_score)
            assert_ok("local_report_score_explanation", bool(local_result["modification_report"].get("score_explanation")))
            assert_old_fields_compatible(local_result)

            os.environ["DEEPSEEK_API_KEY"] = "fake-key"
            os.environ.pop("OPENAI_API_KEY", None)
            language_reviewer.call_ai_language_review = fake_ai_success
            ai_result = run_paper_agent(paper, output_dir, mode="ai")
            ai_score = ai_result["score_breakdown"]
            assert_ok("ai_status_ok", ai_result.get("status") == "ok", ai_result.get("status"))
            assert_ok("ai_used_true", ai_score["ai_used"] is True, ai_score)
            assert_ok("ai_language_score_reference_only", ai_score["ai_language_score"] == ai_score["ai_score"], ai_score)
            assert_ok("ai_final_is_format_score", ai_score["final_score"] == ai_score["format_score"], ai_score)
            assert_ok("ai_score_lower_not_lower_final", ai_score["ai_language_score"] < ai_score["format_score"], ai_score)
            assert_ok("ai_score_explanation_present", "AI语言评分仅作参考" in ai_score["score_explanation"], ai_score)
            assert_old_fields_compatible(ai_result)

            language_reviewer.call_ai_language_review = fake_ai_failure
            fallback_result = run_paper_agent(paper, output_dir, mode="ai")
            fallback_score = fallback_result["score_breakdown"]
            assert_ok("fallback_status_ok", fallback_result.get("status") == "ok", fallback_result.get("status"))
            assert_ok("fallback_ai_score_null", fallback_score["ai_score"] is None, fallback_score)
            assert_ok("fallback_ai_used_false", fallback_score["ai_used"] is False, fallback_score)
            assert_ok("fallback_final_is_format_score", fallback_score["final_score"] == fallback_score["format_score"], fallback_score)
            assert_old_fields_compatible(fallback_result)
    finally:
        language_reviewer.call_ai_language_review = original_ai_call
        os.environ.pop("DEEPSEEK_API_KEY", None)
        os.environ.pop("OPENAI_API_KEY", None)

    print("SCORE_CONSISTENCY PASS")


if __name__ == "__main__":
    main()
