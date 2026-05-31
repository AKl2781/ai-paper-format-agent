from __future__ import annotations

from services.docx_analyzer import analyze_references


def assert_equal(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name} FAIL expected={expected!r} actual={actual!r}")
    print(f"{name} PASS")


def main() -> None:
    no_section = analyze_references(["论文标题", "正文没有参考文献章节。"])
    assert_equal("no_reference_section", no_section["has_reference_section"], False)
    assert_equal("no_reference_count", no_section["reference_count"], 0)

    continuous = analyze_references(["正文引用[1]和[2]。", "参考文献", "[1] 张三. A.", "[2] 李四. B."])
    assert_equal("continuous_numbers", continuous["numbering_gaps"], [])
    assert_equal("continuous_missing", continuous["missing_reference_numbers"], [])
    assert_equal("continuous_uncited", continuous["uncited_reference_numbers"], [])

    gap = analyze_references(["正文引用[1]和[3]。", "参考文献", "[1] 张三. A.", "[3] 王五. C."])
    assert_equal("numbering_gap", gap["numbering_gaps"], [2])

    duplicate = analyze_references(["正文引用[1]。", "参考文献", "[1] 张三. A.", "[1] 李四. B."])
    assert_equal("duplicate_number", duplicate["duplicate_reference_numbers"], [1])

    missing_reference = analyze_references(["正文引用[2]。", "参考文献", "[1] 张三. A."])
    assert_equal("missing_reference_number", missing_reference["missing_reference_numbers"], [2])

    uncited_reference = analyze_references(["正文引用[1]。", "参考文献", "[1] 张三. A.", "[2] 李四. B."])
    assert_equal("uncited_reference_number", uncited_reference["uncited_reference_numbers"], [2])

    print("REFERENCE_CHECKER PASS")


if __name__ == "__main__":
    main()
