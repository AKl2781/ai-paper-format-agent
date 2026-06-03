from __future__ import annotations

from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
import re
import time
from typing import Any

from .docx_analyzer import extract_paragraph_text


MAX_PARAGRAPHS_FOR_COMPARISON = 300
MAX_SIMILARITY_COMPARISONS = 30000
MAX_SEQUENCE_MATCHER_PAIRS = 3000
REPEAT_RISK_TIME_BUDGET_SECONDS = 25.0
SMALL_DOCUMENT_PARAGRAPH_LIMIT = 80


def check_repeat_risk(path: Path) -> dict[str, Any]:
    try:
        paragraphs = [item for item in extract_paragraph_text(path) if len(item) >= 20]
        sampled_paragraphs = sample_paragraphs(paragraphs, MAX_PARAGRAPHS_FOR_COMPARISON)
        sentences = split_sentences("\n".join(text for _, text in sampled_paragraphs))
        similar_paragraphs, comparison_count, comparison_limited = find_similar_paragraphs(
            sampled_paragraphs,
            max_comparisons=MAX_SIMILARITY_COMPARISONS,
        )
        duplicate_sentences = find_duplicate_sentences(sentences)
        truncated = (
            len(paragraphs) > len(sampled_paragraphs)
            or comparison_limited
            or comparison_count >= MAX_SIMILARITY_COMPARISONS
        )
    except Exception as exc:
        return build_fallback_repeat_risk(exc)

    risk_score = min(100, len(similar_paragraphs) * 18 + len(duplicate_sentences) * 12)
    if risk_score >= 55:
        level = "高"
    elif risk_score >= 25:
        level = "中"
    else:
        level = "低"

    return {
        "name": "重复风险检测",
        "description": "相似度预检，不等同于任何正式查重系统。",
        "level": level,
        "score": risk_score,
        "score_for_quality": max(60, 94 - risk_score),
        "similar_paragraphs": similar_paragraphs[:8],
        "duplicate_sentences": duplicate_sentences[:8],
        "suggestions": build_suggestions(level, similar_paragraphs, duplicate_sentences),
        "truncated": truncated,
        "sampled_paragraphs": len(sampled_paragraphs),
        "total_paragraphs": len(paragraphs),
        "max_comparisons": MAX_SIMILARITY_COMPARISONS,
    }


def build_fallback_repeat_risk(error: Exception) -> dict[str, Any]:
    return {
        "name": "重复风险检测",
        "description": "相似度预检，不等同于任何正式查重系统。",
        "level": "低",
        "score": 0,
        "score_for_quality": 94,
        "similar_paragraphs": [],
        "duplicate_sentences": [],
        "suggestions": [
            "重复风险检测未能完成，已按低风险占位继续主流程；提交前建议人工复核重复表述。",
        ],
        "truncated": False,
        "sampled_paragraphs": 0,
        "total_paragraphs": 0,
        "max_comparisons": MAX_SIMILARITY_COMPARISONS,
        "error": str(error),
    }


def sample_paragraphs(paragraphs: list[str], limit: int) -> list[tuple[int, str]]:
    indexed = list(enumerate(paragraphs, start=1))
    if len(indexed) <= limit:
        return indexed
    if limit <= 1:
        return indexed[:limit]

    step = (len(indexed) - 1) / (limit - 1)
    sampled: list[tuple[int, str]] = []
    seen_indices: set[int] = set()
    for sample_index in range(limit):
        source_index = round(sample_index * step)
        if source_index in seen_indices:
            continue
        seen_indices.add(source_index)
        sampled.append(indexed[source_index])
    return sampled


def find_similar_paragraphs(
    paragraphs: list[tuple[int, str]],
    max_comparisons: int = MAX_SIMILARITY_COMPARISONS,
) -> tuple[list[dict[str, Any]], int, bool]:
    results: list[dict[str, Any]] = []
    comparison_count = 0
    sequence_count = 0
    comparison_limited = False
    deadline = time.perf_counter() + REPEAT_RISK_TIME_BUDGET_SECONDS
    prepared = [(number, text, build_paragraph_profile(text)) for number, text in paragraphs]
    small_document = len(paragraphs) <= SMALL_DOCUMENT_PARAGRAPH_LIMIT
    for i, (left_number, left) in enumerate(paragraphs):
        for j in range(i + 1, len(paragraphs)):
            if (
                comparison_count >= max_comparisons
                or (not small_document and sequence_count >= MAX_SEQUENCE_MATCHER_PAIRS)
                or time.perf_counter() >= deadline
            ):
                comparison_limited = True
                return sorted(results, key=lambda item: item["similarity"], reverse=True), comparison_count, comparison_limited
            comparison_count += 1
            left_number, left, left_profile = prepared[i]
            right_number, right, right_profile = prepared[j]
            if not small_document and not is_similarity_candidate(left_profile, right_profile):
                continue
            sequence_count += 1
            ratio = SequenceMatcher(None, normalize(left), normalize(right)).ratio()
            if ratio >= 0.72:
                results.append(
                    {
                        "paragraph_a": left_number,
                        "paragraph_b": right_number,
                        "similarity": round(ratio, 2),
                        "preview": left[:90],
                    }
                )
    return sorted(results, key=lambda item: item["similarity"], reverse=True), comparison_count, comparison_limited


def build_paragraph_profile(text: str) -> dict[str, Any]:
    normalized = normalize(text)
    chars = {char for char in normalized if not char.isdigit()}
    tokens = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]{2,}", normalized))
    if not tokens:
        tokens = {normalized[index : index + 2] for index in range(max(0, len(normalized) - 1))}
    return {
        "length": len(normalized),
        "chars": chars,
        "tokens": tokens,
    }


def is_similarity_candidate(left: dict[str, Any], right: dict[str, Any]) -> bool:
    left_length = left["length"]
    right_length = right["length"]
    if not left_length or not right_length:
        return False

    length_gap = abs(left_length - right_length) / max(left_length, right_length)
    if length_gap > 0.45:
        return False

    char_overlap = overlap_ratio(left["chars"], right["chars"])
    if char_overlap < 0.45:
        return False

    token_overlap = overlap_ratio(left["tokens"], right["tokens"])
    return token_overlap >= 0.18 or (char_overlap >= 0.68 and length_gap <= 0.25)


def overlap_ratio(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    return len(left & right) / min(len(left), len(right))


def find_duplicate_sentences(sentences: list[str]) -> list[dict[str, Any]]:
    normalized = [normalize(sentence) for sentence in sentences if len(normalize(sentence)) >= 12]
    counts = Counter(normalized)
    return [{"sentence": sentence[:100], "count": count} for sentence, count in counts.items() if count > 1]


def split_sentences(text: str) -> list[str]:
    return [item.strip() for item in re.split(r"[。！？!?；;]\s*", text) if item.strip()]


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def build_suggestions(level: str, similar_paragraphs: list[dict[str, Any]], duplicate_sentences: list[dict[str, Any]]) -> list[str]:
    suggestions = [
        "对重复表述较多的段落重新组织论证顺序，避免只替换同义词。",
        "保留必要术语，优先改写解释、例证、过渡句和总结句。",
    ]
    if similar_paragraphs:
        suggestions.append("相似段落建议合并或拆分，减少同一观点的反复铺陈。")
    if duplicate_sentences:
        suggestions.append("重复句子建议保留最准确的一处，其余位置改为承接句或删减。")
    if level == "低":
        suggestions.append("当前为低风险预检，提交前仍建议人工通读确认引用和原文边界。")
    return suggestions
