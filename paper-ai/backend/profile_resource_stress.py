from __future__ import annotations

import argparse
import json
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from docx import Document

from services.document_classifier import classify_document
from services.docx_analyzer import analyze_docx
from services.docx_formatter import (
    apply_normal_style,
    apply_page_setup,
    apply_paragraph_styles,
    apply_table_styles,
    clean_document_text,
    split_long_paragraphs,
    split_mixed_heading_paragraphs,
)
from services.paper_agent import build_modification_report
from services.plagiarism_checker import check_repeat_risk
from services.preview_service import build_docx_preview


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORT_DIR = BASE_DIR / "regression_results"


@dataclass
class Timing:
    name: str
    seconds: float
    detail: str = ""


class Profiler:
    def __init__(self, checkpoint_path: Path | None = None) -> None:
        self.timings: list[Timing] = []
        self.checkpoint_path = checkpoint_path

    def measure(self, name: str, fn: Callable[[], Any], detail: str = "") -> Any:
        start = time.perf_counter()
        result = fn()
        elapsed = time.perf_counter() - start
        self.timings.append(Timing(name=name, seconds=elapsed, detail=detail))
        print(f"{name}: {elapsed:.3f}s {detail}", flush=True)
        self.write_checkpoint(status=f"completed:{name}")
        return result

    def add(self, name: str, seconds: float, detail: str = "") -> None:
        self.timings.append(Timing(name=name, seconds=seconds, detail=detail))
        print(f"{name}: {seconds:.3f}s {detail}", flush=True)
        self.write_checkpoint(status=f"completed:{name}")

    def write_checkpoint(self, status: str) -> None:
        if not self.checkpoint_path:
            return
        payload = {
            "status": status,
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "timings": [
                {"name": item.name, "seconds": round(item.seconds, 3), "detail": item.detail}
                for item in self.timings
            ],
        }
        self.checkpoint_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile heavy DOCX local Agent stages.")
    parser.add_argument(
        "--source",
        default=str(UPLOAD_DIR / "realistic_heavy_thesis.docx"),
        help="Source DOCX path. Defaults to backend/uploads/realistic_heavy_thesis.docx.",
    )
    parser.add_argument(
        "--json-out",
        default="",
        help="Optional JSON report path. Defaults to backend/regression_results/profile_<timestamp>.json.",
    )
    parser.add_argument(
        "--checkpoint-out",
        default="",
        help="Optional checkpoint JSON path. Defaults to backend/regression_results/profile_checkpoint_<timestamp>.json.",
    )
    return parser.parse_args()


def output_path(source: Path, suffix: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return OUTPUT_DIR / f"{source.stem}_{suffix}_profile_{timestamp}.docx"


def profile_formatter(source: Path, output: Path, profiler: Profiler) -> tuple[list[str], dict[str, float]]:
    sub_timings: dict[str, float] = {}

    def substep(name: str, fn: Callable[[], Any]) -> Any:
        start = time.perf_counter()
        result = fn()
        sub_timings[name] = time.perf_counter() - start
        print(f"  formatter.{name}: {sub_timings[name]:.3f}s", flush=True)
        return result

    start = time.perf_counter()
    document = substep("load_document", lambda: Document(source))
    applied: list[str] = []
    applied.extend(substep("clean_document_text", lambda: clean_document_text(document)))
    applied.extend(substep("split_mixed_heading_paragraphs", lambda: split_mixed_heading_paragraphs(document)))
    substep("apply_page_setup", lambda: apply_page_setup(document, None))
    substep("apply_normal_style", lambda: apply_normal_style(document, None))
    applied.extend(substep("split_long_paragraphs", lambda: split_long_paragraphs(document)))
    substep("apply_paragraph_styles", lambda: apply_paragraph_styles(document, None))
    substep("apply_table_styles", lambda: apply_table_styles(document))
    applied.append("Used general thesis formatting rules because no template was provided.")
    applied.append("Normalized body spacing, indentation, paragraph spacing, and heading levels.")
    if document.tables:
        applied.append("Normalized table text alignment and spacing.")

    save_start = time.perf_counter()
    document.save(output)
    save_elapsed = time.perf_counter() - save_start
    sub_timings["docx_save"] = save_elapsed
    total = time.perf_counter() - start
    profiler.add("formatter", total, f"format_changes={len(applied)}")
    profiler.add("docx_save", save_elapsed, f"output={output.name}")
    return applied, sub_timings


def make_report_dict(
    source: Path,
    formatted_path: Path,
    profiler: Profiler,
    formatter_subtimings: dict[str, float],
    classification: dict[str, Any],
    before_repeat: dict[str, Any],
    repeat_risk: dict[str, Any],
    before_analysis: dict[str, Any],
    after_analysis: dict[str, Any],
    modification_report: dict[str, Any],
    preview: dict[str, str],
    download_bytes: int,
) -> dict[str, Any]:
    timings = [
        {"name": item.name, "seconds": round(item.seconds, 3), "detail": item.detail}
        for item in profiler.timings
    ]
    top3 = sorted(timings, key=lambda item: item["seconds"], reverse=True)[:3]
    breakdown = after_analysis["report"]["score_breakdown"]
    return {
        "source": str(source),
        "formatted_output": str(formatted_path),
        "source_size_bytes": source.stat().st_size,
        "output_size_bytes": formatted_path.stat().st_size,
        "classification": {
            "document_type": classification.get("document_type"),
            "label": classification.get("label"),
            "confidence": classification.get("confidence"),
        },
        "before_score": before_analysis["report"]["score"],
        "after_score": after_analysis["report"]["score"],
        "score_breakdown": breakdown,
        "local_mode_checks": {
            "ai_score_null": breakdown.get("ai_score") is None,
            "ai_used_false": breakdown.get("ai_used") is False,
        },
        "repeat_risk": {
            "before": {
                "level": before_repeat.get("level"),
                "score": before_repeat.get("score"),
                "truncated": before_repeat.get("truncated"),
                "sampled_paragraphs": before_repeat.get("sampled_paragraphs"),
                "total_paragraphs": before_repeat.get("total_paragraphs"),
                "max_comparisons": before_repeat.get("max_comparisons"),
            },
            "after": {
                "level": repeat_risk.get("level"),
                "score": repeat_risk.get("score"),
                "truncated": repeat_risk.get("truncated"),
                "sampled_paragraphs": repeat_risk.get("sampled_paragraphs"),
                "total_paragraphs": repeat_risk.get("total_paragraphs"),
                "max_comparisons": repeat_risk.get("max_comparisons"),
            },
        },
        "modification_report": {
            "change_counts": modification_report.get("change_counts"),
            "manual_review_count": len(modification_report.get("manual_review_items") or []),
        },
        "preview": {
            "title": preview.get("title"),
            "html_length": len(preview.get("html") or ""),
        },
        "download_prepare": {
            "bytes_read": download_bytes,
        },
        "formatter_subtimings": {key: round(value, 3) for key, value in formatter_subtimings.items()},
        "timings": timings,
        "top3": top3,
    }


def print_table(report: dict[str, Any]) -> None:
    print("\nStage timings")
    print("| Stage | Seconds | Detail |")
    print("|---|---:|---|")
    for item in report["timings"]:
        print(f"| {item['name']} | {item['seconds']:.3f} | {item['detail']} |")

    print("\nFormatter subtimings")
    print("| Substage | Seconds |")
    print("|---|---:|")
    for name, seconds in report["formatter_subtimings"].items():
        print(f"| {name} | {seconds:.3f} |")

    print("\nTop 3 Bottlenecks")
    print("| Rank | Module | Seconds |")
    print("|---:|---|---:|")
    for index, item in enumerate(report["top3"], start=1):
        print(f"| {index} | {item['name']} | {item['seconds']:.3f} |")

    checks = report["local_mode_checks"]
    print("\nLocal mode checks")
    print(f"ai_score_null: {'PASS' if checks['ai_score_null'] else 'FAIL'}")
    print(f"ai_used_false: {'PASS' if checks['ai_used_false'] else 'FAIL'}")


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    if not source.exists():
        raise FileNotFoundError(f"Source DOCX not found: {source}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    checkpoint_path = (
        Path(args.checkpoint_out)
        if args.checkpoint_out
        else REPORT_DIR / f"profile_checkpoint_{timestamp}.json"
    )
    profiler = Profiler(checkpoint_path=checkpoint_path)

    upload_copy = OUTPUT_DIR / f"{source.stem}_profile_upload_copy.docx"
    profiler.measure("file_upload_read", lambda: shutil.copy2(source, upload_copy), f"bytes={source.stat().st_size}")
    profiler.measure("docx_read_presence_check", lambda: source.exists(), source.name)
    classification = profiler.measure("document_classification", lambda: classify_document(source))
    before_repeat = profiler.measure("plagiarism_checker_before", lambda: check_repeat_risk(source))
    before_analysis = profiler.measure(
        "analyzer_before",
        lambda: analyze_docx(source, repeat_score=before_repeat["score_for_quality"]),
    )
    formatted_path = output_path(source, "formatted")
    format_log, formatter_subtimings = profile_formatter(source, formatted_path, profiler)
    profiler.measure(
        "language_review",
        lambda: {"mode": "local", "error": None, "suggestions": [], "ai_scores": None, "ai_added_value": []},
        "local mode skipped",
    )
    language_log: list[str] = []
    repeat_risk = profiler.measure("plagiarism_checker_after", lambda: check_repeat_risk(formatted_path))
    after_analysis = profiler.measure(
        "analyzer_after",
        lambda: analyze_docx(formatted_path, repeat_score=repeat_risk["score_for_quality"], ai_scores=None),
    )
    modification_report = profiler.measure(
        "report_generation",
        lambda: build_modification_report(before_analysis, after_analysis, format_log, language_log, repeat_risk, None),
    )
    preview = profiler.measure("preview_generation", lambda: build_docx_preview(formatted_path))
    download_bytes = profiler.measure("download_prepare", lambda: len(formatted_path.read_bytes()), formatted_path.name)

    report = make_report_dict(
        source=source,
        formatted_path=formatted_path,
        profiler=profiler,
        formatter_subtimings=formatter_subtimings,
        classification=classification,
        before_repeat=before_repeat,
        repeat_risk=repeat_risk,
        before_analysis=before_analysis,
        after_analysis=after_analysis,
        modification_report=modification_report,
        preview=preview,
        download_bytes=download_bytes,
    )

    if args.json_out:
        json_path = Path(args.json_out)
    else:
        json_path = REPORT_DIR / f"profile_resource_stress_{timestamp}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print_table(report)
    print(f"\nJSON report: {json_path}")


if __name__ == "__main__":
    main()
