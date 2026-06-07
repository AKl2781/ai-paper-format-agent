from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from services.document_classifier import classify_document
from services.paper_agent import run_paper_agent
from services.preview_service import build_docx_preview


BASE_DIR = Path(__file__).resolve().parent
TEST_DOCS_DIR = BASE_DIR / "test_documents"
OUTPUT_DIR = BASE_DIR / "outputs"
RESULTS_DIR = BASE_DIR / "regression_results"
DEFAULT_MANIFEST = TEST_DOCS_DIR / "manifest.csv"

SIZE_BUCKETS = (
    ("small", 1 * 1024 * 1024),
    ("medium", 10 * 1024 * 1024),
)
BOUNDARY_MARKERS = {"classification_boundary", "non_blocking_boundary"}
EXPLAINABLE_CLASSIFICATION_BOUNDARIES = {
    frozenset({"academic_paper", "lab_report"}),
}


def parse_bool(value: object, default: bool = False) -> bool:
    if value is None or value == "":
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def size_bucket(size_bytes: int) -> str:
    for name, limit in SIZE_BUCKETS:
        if size_bytes < limit:
            return name
    return "large"


def resolve_manifest_path(value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path.resolve()


def resolve_test_path(value: str) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = TEST_DOCS_DIR / path
    return path.resolve()


def expected_document_types(value: str) -> set[str]:
    return {item.strip() for item in value.split("|") if item.strip()}


def risk_markers(value: str) -> set[str]:
    return {item.strip() for item in value.split(";") if item.strip()}


def is_boundary_case(row: dict[str, str]) -> bool:
    return bool(risk_markers(row.get("known_risks", "")) & BOUNDARY_MARKERS)


def is_explainable_boundary(expected_types: set[str], actual_type: str | None) -> bool:
    if not actual_type:
        return False
    return any(
        actual_type in boundary and bool(expected_types & boundary)
        for boundary in EXPLAINABLE_CLASSIFICATION_BOUNDARIES
    )


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def compact_result(result: dict[str, Any]) -> dict[str, Any]:
    if result.get("status") != "ok":
        return {
            "status": result.get("status"),
            "failed_step": result.get("failed_step"),
            "error": result.get("error"),
            "message": result.get("message"),
            "classification": result.get("classification"),
        }
    return {
        "status": result.get("status"),
        "mode": result.get("mode"),
        "filename": result.get("filename"),
        "before_score": result.get("before_score"),
        "after_score": result.get("after_score"),
        "score_breakdown": result.get("score_breakdown"),
        "classification": result.get("classification"),
        "repeat_risk": {
            "level": (result.get("repeat_risk") or {}).get("level"),
            "score": (result.get("repeat_risk") or {}).get("score"),
        },
        "change_counts": (result.get("modification_report") or {}).get("change_counts"),
        "manual_review_items": (result.get("modification_report") or {}).get("manual_review_items"),
    }


def expected_status(row: dict[str, str], key: str, actual: bool) -> bool:
    return actual if parse_bool(row.get(key), default=True) else True


def run_case(row: dict[str, str], *, mode: str, confirm_non_paper: bool) -> dict[str, Any]:
    started = time.perf_counter()
    case_id = row["case_id"]
    paper_path = resolve_test_path(row["file_name"])
    template_path = resolve_test_path(row.get("template_file", ""))
    expected_type = row.get("document_type", "")
    result: dict[str, Any] = {}
    preview_ok = False
    download_ok = False
    report_ok = False
    output_path: Path | None = None
    errors: list[str] = []
    boundary_warnings: list[str] = []

    if not paper_path or not paper_path.exists():
        return {
            "case_id": case_id,
            "file_name": row.get("file_name"),
            "status": "FAIL",
            "errors": [f"missing paper file: {row.get('file_name')}"],
            "elapsed_seconds": round(time.perf_counter() - started, 3),
        }

    if template_path and not template_path.exists():
        errors.append(f"missing template file: {row.get('template_file')}")
        template_path = None

    classification = classify_document(paper_path)
    classification_ok = not parse_bool(row.get("expected_classification_success"), default=True)
    if parse_bool(row.get("expected_classification_success"), default=True):
        accepted_types = expected_document_types(expected_type)
        actual_type = classification.get("document_type")
        classification_ok = actual_type in accepted_types
        if not classification_ok:
            message = f"classification expected {expected_type}, got {actual_type}"
            if is_boundary_case(row) and is_explainable_boundary(accepted_types, actual_type):
                boundary_warnings.append(message)
            else:
                errors.append(message)

    allow_non_paper = confirm_non_paper and classification.get("requires_confirmation") is True
    result = run_paper_agent(
        paper_path=paper_path,
        template_path=template_path,
        output_dir=OUTPUT_DIR,
        allow_non_paper=allow_non_paper,
        mode=mode,
    )
    agent_ok = result.get("status") == "ok"
    if not agent_ok:
        errors.append(f"agent status: {result.get('status')}")

    if agent_ok:
        report = result.get("modification_report") or {}
        report_ok = bool(report.get("summary")) and bool(report.get("change_counts"))
        if not expected_status(row, "expected_report", report_ok):
            errors.append("missing modification report")

        filename = result.get("filename")
        output_path = OUTPUT_DIR / Path(filename).name if filename else None
        download_ok = bool(output_path and output_path.exists() and output_path.stat().st_size > 0)
        if not expected_status(row, "expected_download", download_ok):
            errors.append("missing output download file")

        if output_path and output_path.exists():
            try:
                preview = build_docx_preview(output_path)
                preview_ok = bool(preview.get("html"))
            except Exception as exc:  # pragma: no cover - recorded in regression output
                errors.append(f"preview error: {exc}")
        if not expected_status(row, "expected_preview", preview_ok):
            errors.append("preview failed")

        manual_review_items = report.get("manual_review_items") or []
        warning_items = report.get("warning_items") or []
        unresolved_issues = report.get("unresolved_issues") or []
        manual_review_ok = bool(manual_review_items or warning_items or unresolved_issues)
        if parse_bool(row.get("expected_manual_review"), default=False) and not manual_review_ok:
            errors.append("expected manual review items")

        if mode == "local":
            breakdown = result.get("score_breakdown") or {}
            if breakdown.get("ai_score") is not None or breakdown.get("ai_used") is not False:
                errors.append("local mode AI fields invalid")

    if errors or not agent_ok:
        status = "FAIL"
    elif boundary_warnings:
        status = "BOUNDARY_WARNING"
    else:
        status = "PASS"
    size_bytes = paper_path.stat().st_size
    elapsed = round(time.perf_counter() - started, 3)
    return {
        "case_id": case_id,
        "file_name": row.get("file_name"),
        "category": row.get("category"),
        "size_bytes": size_bytes,
        "size_bucket": size_bucket(size_bytes),
        "expected_document_type": expected_type,
        "actual_document_type": classification.get("document_type"),
        "requires_confirmation": classification.get("requires_confirmation"),
        "confirmed_non_paper": allow_non_paper,
        "mode": mode,
        "status": status,
        "classification_ok": classification_ok,
        "boundary_warning": bool(boundary_warnings),
        "agent_ok": agent_ok,
        "report_ok": report_ok,
        "preview_ok": preview_ok,
        "download_ok": download_ok,
        "output_file": output_path.name if output_path else "",
        "before_score": result.get("before_score"),
        "after_score": result.get("after_score"),
        "ai_score": (result.get("score_breakdown") or {}).get("ai_score") if agent_ok else None,
        "ai_used": (result.get("score_breakdown") or {}).get("ai_used") if agent_ok else None,
        "elapsed_seconds": elapsed,
        "errors": errors,
        "boundary_warnings": boundary_warnings,
        "raw_result": compact_result(result),
    }


def write_results(run_dir: Path, cases: list[dict[str, Any]], manifest: Path) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    cases_dir = run_dir / "cases"
    cases_dir.mkdir(exist_ok=True)

    summary = {
        "manifest": str(manifest),
        "case_count": len(cases),
        "pass_count": sum(1 for item in cases if item["status"] == "PASS"),
        "boundary_warning_count": sum(1 for item in cases if item["status"] == "BOUNDARY_WARNING"),
        "fail_count": sum(1 for item in cases if item["status"] == "FAIL"),
        "total_elapsed_seconds": round(sum(float(item["elapsed_seconds"]) for item in cases), 3),
        "size_buckets": {
            bucket: sum(1 for item in cases if item.get("size_bucket") == bucket)
            for bucket in ["small", "medium", "large"]
        },
        "cases": cases,
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    csv_fields = [
        "case_id",
        "file_name",
        "category",
        "size_bytes",
        "size_bucket",
        "expected_document_type",
        "actual_document_type",
        "requires_confirmation",
        "confirmed_non_paper",
        "mode",
        "status",
        "classification_ok",
        "boundary_warning",
        "agent_ok",
        "report_ok",
        "preview_ok",
        "download_ok",
        "output_file",
        "before_score",
        "after_score",
        "ai_score",
        "ai_used",
        "elapsed_seconds",
        "errors",
        "boundary_warnings",
    ]
    with (run_dir / "summary.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for item in cases:
            row = {key: item.get(key, "") for key in csv_fields}
            row["errors"] = "; ".join(item.get("errors") or [])
            row["boundary_warnings"] = "; ".join(item.get("boundary_warnings") or [])
            writer.writerow(row)

    for item in cases:
        case_path = cases_dir / f"{item['case_id']}.json"
        case_path.write_text(json.dumps(item, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run manifest-driven DOCX regression cases.")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST.relative_to(BASE_DIR)))
    parser.add_argument("--mode", choices=["local", "ai"], default="local")
    parser.add_argument("--case-id", action="append", default=[])
    parser.add_argument("--category", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--no-confirm-non-paper",
        action="store_true",
        help="Do not auto-confirm non-paper documents after classification.",
    )
    parser.add_argument("--run-id", default=datetime.now().strftime("%Y%m%d_%H%M%S"))
    args = parser.parse_args()

    manifest = resolve_manifest_path(args.manifest)
    rows = read_manifest(manifest)
    if args.case_id:
        selected = set(args.case_id)
        rows = [row for row in rows if row.get("case_id") in selected]
    if args.category:
        selected_categories = set(args.category)
        rows = [row for row in rows if row.get("category") in selected_categories]
    if args.limit:
        rows = rows[: args.limit]

    cases = [
        run_case(row, mode=args.mode, confirm_non_paper=not args.no_confirm_non_paper)
        for row in rows
    ]
    run_dir = RESULTS_DIR / args.run_id
    write_results(run_dir, cases, manifest)

    pass_count = sum(1 for item in cases if item["status"] == "PASS")
    boundary_warning_count = sum(1 for item in cases if item["status"] == "BOUNDARY_WARNING")
    fail_count = sum(1 for item in cases if item["status"] == "FAIL")
    print(f"Run directory: {run_dir}")
    print(f"Cases: {len(cases)} PASS={pass_count} BOUNDARY_WARNING={boundary_warning_count} FAIL={fail_count}")
    if boundary_warning_count:
        for item in cases:
            if item["status"] == "BOUNDARY_WARNING":
                print(f"BOUNDARY_WARNING {item['case_id']}: {'; '.join(item.get('boundary_warnings') or [])}")
    if fail_count:
        for item in cases:
            if item["status"] == "FAIL":
                print(f"FAIL {item['case_id']}: {'; '.join(item.get('errors') or [])}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
