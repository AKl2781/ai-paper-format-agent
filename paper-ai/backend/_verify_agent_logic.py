from fastapi.testclient import TestClient
from docx import Document
from main import app
import io


def docx_bytes(paragraphs):
    doc = Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()


client = TestClient(app)

course_doc = docx_bytes(
    [
        "课程名称：人工智能导论",
        "学号：20260001",
        "班级：计科一班",
        "作业题目：课程作业一",
        "思考题：请分析模型效果。",
    ]
)
academic_doc = docx_bytes(
    [
        "题目：人工智能论文格式研究",
        "摘要：本文研究论文格式自动修改。",
        "关键词：论文；格式；Agent",
        "引言：本文介绍研究背景。",
        "结论：本文完成实验。",
        "参考文献：[1] 张三. 示例文献.",
    ]
)

res = client.post(
    "/document/classify",
    files={"paper": ("course.docx", course_doc, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
)
print("classify_course", res.status_code, res.json())

res = client.post(
    "/agent/run",
    files={"paper": ("course.docx", course_doc, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
)
body = res.json()
print("agent_course_no_confirm", res.status_code, body.get("status"), body.get("requires_confirmation"), body.get("classification"))

res = client.post(
    "/agent/run",
    data={"mode": "local", "allow_non_paper": "true"},
    files={"paper": ("course.docx", course_doc, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
)
body = res.json()
print("agent_course_confirm", res.status_code, body.get("status"), body.get("score_breakdown"))

res = client.post(
    "/agent/run",
    data={"mode": "local"},
    files={"paper": ("paper.docx", academic_doc, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
)
body = res.json()
print("agent_academic_local", res.status_code, body.get("status"), body.get("classification"), body.get("score_breakdown"))
