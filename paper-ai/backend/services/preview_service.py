from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from docx import Document


def build_docx_preview(path: Path) -> dict[str, str]:
    document = Document(path)
    title = find_title(document)
    html_parts: list[str] = []

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        tag = paragraph_tag(paragraph, text)
        content = render_runs(paragraph)
        align = alignment_class(paragraph.alignment)
        html_parts.append(f'<{tag} class="docx-paragraph {align}">{content}</{tag}>')

    for table in document.tables:
        html_parts.append(render_table(table))

    return {
        "title": title,
        "html": "\n".join(html_parts) or "<p>未能读取到可预览内容。</p>",
    }


def find_title(document) -> str:
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:
            return text[:120]
    return "论文预览"


def paragraph_tag(paragraph, text: str) -> str:
    style_name = paragraph.style.name if paragraph.style else ""
    if style_name.startswith("Title") or style_name.startswith("论文标题"):
        return "h1"
    if style_name.startswith("Heading 1") or style_name.startswith("标题 1") or is_main_heading(text):
        return "h2"
    if style_name.startswith("Heading 2") or style_name.startswith("标题 2"):
        return "h3"
    if style_name.startswith("Heading 3") or style_name.startswith("标题 3"):
        return "h4"
    return "p"


def is_main_heading(text: str) -> bool:
    return text in {"摘要", "关键词", "引言", "绪论", "结论", "参考文献"} or text.startswith(("一、", "二、", "三、", "四、", "五、"))


def render_runs(paragraph) -> str:
    if not paragraph.runs:
        return escape(paragraph.text)
    parts: list[str] = []
    for run in paragraph.runs:
        text = escape(run.text)
        if not text:
            continue
        if run.bold:
            text = f"<strong>{text}</strong>"
        if run.italic:
            text = f"<em>{text}</em>"
        parts.append(text)
    return "".join(parts) or escape(paragraph.text)


def render_table(table) -> str:
    rows = []
    for row in table.rows:
        cells = "".join(f"<td>{escape(cell.text.strip())}</td>" for cell in row.cells)
        rows.append(f"<tr>{cells}</tr>")
    return f'<table class="docx-table">{"".join(rows)}</table>'


def alignment_class(alignment: Any) -> str:
    name = str(alignment)
    if "CENTER" in name:
        return "align-center"
    if "RIGHT" in name:
        return "align-right"
    if "JUSTIFY" in name:
        return "align-justify"
    return "align-left"
