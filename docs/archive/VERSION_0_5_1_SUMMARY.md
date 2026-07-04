# v0.5.1 Summary: real-doc-regression-boundary-pass

冻结日期：2026-06-07

## 版本结论

`v0.5.1 / real-doc-regression-boundary-pass` 是当前稳定测试版。

本版本没有修改 formatter、agent、API、前端、分类器业务逻辑；变更集中在真实文档回归体系、测试元数据、回归报告和状态文档。

最终结论：

- blocking FAIL：0
- `manifest.csv`：PASS
- `generated_manifest.csv`：PASS with boundary warnings
- `heavy_manifest.csv`：PASS
- smoke：PASS

建议打 Git tag：

```text
v0.5.1-heavy-regression-pass
```

## 当前能力

### 主链路能力

- 文档上传、分类、local Agent、格式修复、评分、报告、预览、下载链路可运行。
- local 模式稳定保持 `ai_score=null`、`ai_used=false`。
- ai 模式具备 LLM / fallback 容错基础，但当前仍主要是词语级增强。

### 格式 Agent 能力

- 标题、正文样式、字体、行距、缩进、页边距基础修复。
- 标题正文混排基础拆分。
- `C-51` 等模板残留基础清理。
- 参考文献与图表编号检查进入报告和人工复查体系。
- 重复风险检测 / 相似度预检具备性能保护。

### 回归体系能力

- `run_real_doc_regression.py` 支持读取 manifest 批量执行分类、Agent、报告、预览、下载和 local AI 字段校验。
- 支持 `PASS`、`BOUNDARY_WARNING`、blocking `FAIL` 区分。
- 支持 small / medium / large 文件大小分桶。
- 支持真实样本、生成样本和 heavy DOCX 压力样本分开回归。

## 本轮回归结果

| 回归项 | 结果 |
| --- | --- |
| `test_documents/manifest.csv` | PASS，10 PASS / 0 boundary warning / 0 FAIL |
| `test_documents/generated_manifest.csv` | PASS with boundary warnings，21 PASS / 3 boundary warning / 0 FAIL |
| `test_documents/heavy_manifest.csv` | PASS，1 PASS / 0 boundary warning / 0 FAIL |
| `test_smoke_agent_flow.py` | PASS |

blocking FAIL：0

boundary_warning：3

3 个 boundary warning 是：

- `reports_001`
- `reports_002`
- `reports_003`

原因：这些样本是 `lab_report` / `academic_paper` 混合结构，manifest 预期为 `lab_report`，实际分类为 `academic_paper`。主链路、报告、预览、下载和 local AI 字段均通过，故不计入 blocking FAIL。

## Heavy DOCX 压力回归

样本：

```text
test_documents/real/realistic_heavy_thesis.docx
```

结果：

| 项目 | 结果 |
| --- | --- |
| 分类结果 | `academic_paper` |
| 耗时 | 57.558s |
| 输出 DOCX | 已生成 |
| 修改报告 | 已生成 |
| 预览 / 下载 | 通过 |
| local `ai_used` | `false` |
| local `ai_score` | `null` |
| 段落 / 表格 / 图片保留 | 2489 / 80 / 100 |
| 超时、内存异常、文件体积异常 | 未发现 |

## 已知边界

1. `generated_manifest.csv` 中 3 个报告类样本仍是分类边界样本，不是功能失败。
2. 当前内容 Agent 仍偏浅，AI 模式主要是少量词语级替换，不能证明深度论文润色能力。
3. 参考文献识别仍可能在复杂真实论文中偏弱。
4. 复杂模板、目录、页眉页脚、脚注、图片题注、公式编号仍受 `python-docx` 能力限制。
5. 在线预览是基础 HTML 结构预览，不追求 Word 完全还原。

## 未解决事项

- 强化报告类 / 论文类边界分类，但要避免误伤理工科论文。
- 增强内容 Agent 的段落级问题识别能力。
- 将 AI 评分和真实修改量进一步绑定。
- 继续补充合法、公开或已授权的真实 DOCX 样本。
- 补齐 medium / large 多样本回归，不只依赖单个 heavy 样本。
- 清理或归档回归输出目录，避免长期堆积。

## 临时输出目录检查

当前存在多个未跟踪的 `regression_results/` 输出目录，例如：

- `20260607_181919/`
- `20260607_182413/`
- `20260607_183251/`
- `20260607_183319/`
- `20260607_184437/`
- `20260607_184455/`
- `20260607_185607/`
- `20260607_185623/`
- `20260607_185651/`
- `codex_*`
- `real_doc_report_*`

建议后续在发布前选择少量代表性结果保留，其他运行产物归档或清理。

本轮不删除这些目录。

## Tag 建议

建议 tag：

```text
v0.5.1-heavy-regression-pass
```

Tag 含义：

- v0.5.1 测试版冻结
- real doc regression 已具备 boundary warning 统计
- heavy DOCX local 回归通过
- blocking FAIL 为 0
