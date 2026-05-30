from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document

from .docx_analyzer import is_section_heading


DEFAULT_TEMPLATE_PROFILE: dict[str, Any] = {
    "margins": {"top": 2.54, "bottom": 2.54, "left": 3.18, "right": 3.18},
    "normal": {"font_name": "宋体", "font_size": 12},
    "body": {
        "alignment": None,
        "line_spacing": 1.5,
        "first_line_indent_cm": 0.74,
        "space_before_pt": 0,
        "space_after_pt": 0,
    },
    "heading": {},
    "warnings": [],
}


def extract_template_profile(path: Path | None) -> dict[str, Any] | None:
    if not path:
        return None

    profile = clone_default_profile()
    profile["filename"] = path.name
    try:
        document = Document(path)
    except Exception:
        profile["warnings"].append("模板文件无法解析，已使用默认论文格式。")
        return profile

    try:
        section = document.sections[0]
        profile["margins"] = {
            "top": safe_margin(section.top_margin.cm, 2.54),
            "bottom": safe_margin(section.bottom_margin.cm, 2.54),
            "left": safe_margin(section.left_margin.cm, 3.18),
            "right": safe_margin(section.right_margin.cm, 3.18),
        }
    except Exception:
        profile["warnings"].append("模板页边距无法完整读取，已使用默认论文页边距。")

    try:
        normal = document.styles["Normal"]
        profile["normal"] = {
            "font_name": normal.font.name or "宋体",
            "font_size": safe_size(point_value(normal.font.size, None), 12),
        }
    except Exception:
        profile["warnings"].append("模板正文样式无法完整读取，已使用默认宋体小四。")

    profile["heading"] = extract_heading_styles(document, profile["warnings"])
    profile["body"] = extract_body_style(document, profile["warnings"])
    return profile


def clone_default_profile() -> dict[str, Any]:
    return {
        "margins": DEFAULT_TEMPLATE_PROFILE["margins"].copy(),
        "normal": DEFAULT_TEMPLATE_PROFILE["normal"].copy(),
        "body": DEFAULT_TEMPLATE_PROFILE["body"].copy(),
        "heading": {},
        "warnings": [],
    }


def extract_heading_styles(document, warnings: list[str]) -> dict[str, Any]:
    headings: dict[str, Any] = {}
    for style_name in ["Heading 1", "Heading 2", "Heading 3", "标题 1", "标题 2", "标题 3"]:
        try:
            style = document.styles[style_name]
        except Exception:
            continue
        headings[style_name] = {
            "font_name": style.font.name or "黑体",
            "font_size": safe_size(point_value(style.font.size, None), None),
            "bold": True if style.font.bold is None else bool(style.font.bold),
        }
    if not headings:
        warnings.append("模板标题样式无法完整读取，已使用默认标题格式。")
    return headings


def extract_body_style(document, warnings: list[str]) -> dict[str, Any]:
    body = DEFAULT_TEMPLATE_PROFILE["body"].copy()
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text or is_section_heading(text):
            continue
        fmt = paragraph.paragraph_format
        body.update(
            {
                "alignment": paragraph.alignment,
                "line_spacing": safe_spacing(fmt.line_spacing, 1.5),
                "first_line_indent_cm": safe_margin(cm_value(fmt.first_line_indent), 0.74),
                "space_before_pt": safe_size(point_value(fmt.space_before, None), 0),
                "space_after_pt": safe_size(point_value(fmt.space_after, None), 0),
            }
        )
        return body
    warnings.append("模板正文段落样式无法读取，已使用默认正文格式。")
    return body


def safe_margin(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if 0 <= number <= 10 else fallback


def safe_size(value: Any, fallback: int | float | None) -> int | float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if 0 <= number <= 96 else fallback


def safe_spacing(value: Any, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return fallback
    return number if 0.8 <= number <= 3 else fallback


def point_value(value, fallback: int | float | None) -> int | float | None:
    if value is None:
        return fallback
    try:
        return value.pt
    except Exception:
        return fallback


def cm_value(value) -> float | None:
    if value is None:
        return None
    try:
        return value.cm
    except Exception:
        return None
