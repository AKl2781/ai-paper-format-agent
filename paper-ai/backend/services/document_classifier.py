from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from docx import Document


TYPE_LABELS = {
    "academic_paper": "标准论文",
    "course_assignment": "课程作业",
    "lab_report": "实验报告",
    "resume": "简历",
    "unknown": "未知文档",
}


ACADEMIC_FEATURE_GROUPS = {
    "标题编号结构": [r"^\s*\d+(\.\d+)*[、.\s]", r"^\s*\d+(?:\.\d+){0,3}\s*(引言|绪论|结论|结语|总结|研究背景|研究方法)"],
    "摘要/关键词": [r"摘要", r"关键词|关键字|Abstract|Keywords"],
    "引言/绪论": [r"引言|绪论|研究背景"],
    "结论/结语/总结": [r"结论|结语|总结"],
    "参考文献/文献引用": [r"参考文献|References", r"\[[0-9]{1,3}\]", r"（[0-9]{4}）"],
}

NON_PAPER_FEATURES = {
    "course_assignment": ["课程名称", "作业", "题目", "学号", "班级", "姓名", "任课教师", "思考题"],
    "lab_report": ["实验目的", "实验内容", "实验步骤", "实验结果", "实验分析", "实验结论", "实验器材"],
    "resume": ["教育经历", "项目经历", "技能", "工作经历", "实习经历", "自我评价", "求职意向"],
}


def classify_document(path: Path) -> dict[str, Any]:
    paragraphs = [p.text.strip() for p in Document(path).paragraphs if p.text.strip()]
    text = "\n".join(paragraphs)

    academic_matches = academic_features(text, paragraphs)
    non_paper_scores = {key: match_features(text, values) for key, values in NON_PAPER_FEATURES.items()}
    best_non_paper = max(non_paper_scores, key=lambda key: len(non_paper_scores[key]))
    best_non_paper_matches = non_paper_scores[best_non_paper]

    if len(academic_matches) >= 2:
        document_type = "academic_paper"
        confidence = max(0.65, min(0.95, 0.5 + len(academic_matches) * 0.1))
        matched_features = academic_matches
    elif len(best_non_paper_matches) >= 3:
        document_type = best_non_paper
        confidence = min(0.95, 0.48 + len(best_non_paper_matches) * 0.08)
        matched_features = best_non_paper_matches
    elif len(paragraphs) >= 8 and len(academic_matches) >= 1 and len(best_non_paper_matches) < 3:
        document_type = "academic_paper"
        confidence = 0.62
        matched_features = academic_matches + ["正文段落数量较多"]
    else:
        document_type = "unknown"
        confidence = 0.4 if paragraphs else 0.2
        matched_features = academic_matches or best_non_paper_matches

    warning = ""
    requires_confirmation = False
    if document_type != "academic_paper":
        warning = f"检测到该文件可能是{TYPE_LABELS[document_type]}，不建议直接强制套用论文格式。"
        requires_confirmation = document_type in {"course_assignment", "lab_report", "resume"} and confidence >= 0.55

    return {
        "document_type": document_type,
        "label": TYPE_LABELS[document_type],
        "confidence": round(confidence, 2),
        "matched_features": matched_features,
        "warning": warning,
        "requires_confirmation": requires_confirmation,
    }


def academic_features(text: str, paragraphs: list[str]) -> list[str]:
    matches: list[str] = []
    for label, patterns in ACADEMIC_FEATURE_GROUPS.items():
        if any(re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) for pattern in patterns):
            matches.append(label)
    if count_heading_like_paragraphs(paragraphs) >= 2 and "标题编号结构" not in matches:
        matches.append("标题编号结构")
    if len(paragraphs) >= 10:
        matches.append("正文段落数量较多")
    return matches


def match_features(text: str, features: list[str]) -> list[str]:
    lowered = text.lower()
    return [feature for feature in features if feature.lower() in lowered]


def count_heading_like_paragraphs(paragraphs: list[str]) -> int:
    count = 0
    for paragraph in paragraphs:
        text = paragraph.strip()
        if not text or len(text) > 60:
            continue
        if re.match(r"^\s*(第[一二三四五六七八九十\d]+[章节]|[一二三四五六七八九十]+[、.．])", text):
            count += 1
            continue
        if re.match(r"^\s*\d+[、.．]\s*\S+", text) or re.match(r"^\s*\d+\.\d+(?:\.\d+){0,2}\s*\S+", text):
            count += 1
    return count
