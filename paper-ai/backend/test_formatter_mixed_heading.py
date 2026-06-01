from pathlib import Path

from docx import Document

from services.docx_formatter import apply_paper_format


def test_split_inline_numbered_heading(tmp_path: Path) -> None:
    source = tmp_path / "inline_heading.docx"
    output = tmp_path / "inline_heading_formatted.docx"

    document = Document()
    document.add_paragraph("测试论文")
    document.add_paragraph(
        "前文介绍了一些压力的表现以及办法。4. 结语：面对高中生的学习压力，文中介绍了压力形成的原因。"
    )
    document.save(source)

    apply_paper_format(source, output)

    paragraphs = [paragraph.text for paragraph in Document(output).paragraphs if paragraph.text.strip()]
    assert "前文介绍了一些压力的表现以及办法。" in paragraphs
    assert "4. 结语" in paragraphs
    assert "面对高中生的学习压力，文中介绍了压力形成的原因。" in paragraphs
