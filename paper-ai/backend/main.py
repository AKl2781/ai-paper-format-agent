from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from services.document_classifier import classify_document
from services.agent_pipeline import run_agent_pipeline
from services.preview_service import build_docx_preview


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
TEMPLATE_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "outputs"

for directory in (UPLOAD_DIR, TEMPLATE_DIR, OUTPUT_DIR):
    directory.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env", override=True, encoding="utf-8-sig")

api_proxy_url = os.getenv("API_PROXY_URL") or os.getenv("DEEPSEEK_PROXY_URL")
if api_proxy_url:
    os.environ["HTTP_PROXY"] = api_proxy_url
    os.environ["HTTPS_PROXY"] = api_proxy_url

app = FastAPI(title="AI Paper Formatting Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/document/classify")
async def classify_uploaded_document(paper: UploadFile = File(...)) -> dict[str, object]:
    paper_path = save_docx(paper, UPLOAD_DIR)
    result = classify_document(paper_path)
    result["filename"] = paper_path.name
    return result


@app.post("/agent/run")
async def run_agent(
    paper: UploadFile = File(...),
    template: UploadFile | None = File(None),
    allow_non_paper: bool = Form(False),
    mode: str = Form("ai"),
) -> dict[str, object]:
    paper_path = save_docx(paper, UPLOAD_DIR)
    template_path = save_docx(template, TEMPLATE_DIR) if template and template.filename else None
    result = run_agent_pipeline(
        paper_path=paper_path,
        template_path=template_path,
        output_dir=OUTPUT_DIR,
        allow_non_paper=allow_non_paper,
        mode=mode,
    )
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result)
    return result


@app.get("/download/{filename}")
def download_file(filename: str) -> FileResponse:
    target = OUTPUT_DIR / Path(filename).name
    if not target.exists():
        raise HTTPException(status_code=404, detail="没有找到生成后的 Word 文件。")
    return FileResponse(
        path=target,
        filename=target.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.get("/preview/{filename}")
def preview_file(filename: str) -> dict[str, str]:
    target = OUTPUT_DIR / Path(filename).name
    if not target.exists():
        raise HTTPException(status_code=404, detail="没有找到可预览的 Word 文件。")
    return build_docx_preview(target)


def save_docx(file: UploadFile, directory: Path) -> Path:
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="只支持 .docx 文件。")
    target = directory / Path(file.filename).name
    target.write_bytes(file.file.read())
    return target
