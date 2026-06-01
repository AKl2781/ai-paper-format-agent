# Deployment Plan

本文档只规划部署方向，不实现 Docker，不新增部署文件。

## 当前部署方式

当前项目以本地开发方式运行：

Backend:

```powershell
cd D:\ai_论文修改格式\paper-ai\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd D:\ai_论文修改格式\paper-ai\frontend
npm install
npm run dev
```

## 未来 Docker 规划

### backend.Dockerfile

规划目标：

- 基于 Python 镜像
- 安装 `paper-ai/backend/requirements.txt`
- 暴露 `8000`
- 启动 `uvicorn main:app --host 0.0.0.0 --port 8000`
- 将 `uploads/`、`outputs/` 和 `templates/` 作为可挂载目录

### frontend.Dockerfile

规划目标：

- 基于 Node.js 镜像
- 安装依赖
- 执行 `npm run build`
- 使用 `npm run start`
- 暴露 `3000`
- 通过环境变量配置后端 API 地址

### docker-compose.yml

规划服务：

- `backend`
- `frontend`

规划挂载：

- `paper-ai/backend/uploads`
- `paper-ai/backend/outputs`
- `paper-ai/backend/templates`

规划网络：

- frontend 访问 backend 内部服务名，例如 `http://backend:8000`
- 浏览器访问 frontend，例如 `http://127.0.0.1:3000`

## 环境变量

Backend:

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DEEPSEEK_MAX_INPUT_CHARS`
- `DEEPSEEK_MAX_OUTPUT_TOKENS`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `API_PROXY_URL`

Frontend:

- 后续建议新增 `NEXT_PUBLIC_API_BASE`

当前前端 API 地址仍写在 `app/page.tsx` 中，Docker 化前应改为环境变量，但该改动不属于本阶段文档整理任务。

## uploads/outputs 持久化

生产或演示环境应持久化：

- `paper-ai/backend/uploads/`
- `paper-ai/backend/outputs/`
- `paper-ai/backend/templates/`

建议策略：

- 定期清理过期上传和输出文件。
- 不把真实用户 DOCX 提交到 git。
- 不把 `.env`、日志、构建产物、上传文件和输出文件打入镜像。

## 部署前检查清单

- Backend `py_compile` 通过。
- `test_smoke_agent_flow.py` 通过。
- `test_reference_checker.py` 通过。
- `test_figure_table_checker.py` 通过。
- `test_agent_orchestrator_trace.py` 通过。
- `test_risk_level_system.py` 通过。
- `test_score_consistency.py` 通过。
- Frontend `npm run build` 通过。
- `/health` 可访问。
- 上传、预览、下载链路可用。
