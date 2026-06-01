# Risk Level System

Risk Level System 用于把参考文献检查和图表编号检查中的问题分层，避免所有提示都被展示成“必须人工复查”。

## RiskLevel

### blocking

阻断级风险。表示当前流程或文档状态不适合继续自动处理，需要用户确认或人工介入。

示例：

- 非论文文档需要用户确认后才能继续
- 后续如果出现不可恢复的文档结构错误，也应归入 blocking

### high_risk

高风险。表示可能影响提交质量或学术规范，需要人工复查。

示例：

- 参考文献重复编号
- 正文引用的参考文献编号不存在
- 图编号重复
- 表编号重复
- 正文引用的图号或表号不存在

### warning

警告。表示建议检查，但不一定影响主流程，也不应默认造成强制人工复查。

示例：

- 缺少参考文献章节
- 参考文献编号跳号
- 文末参考文献未在正文引用
- 图编号跳号
- 表编号跳号

### info

提示。表示更偏产品说明或弱提示，通常不代表错误。

示例：

- Word 有表格但没有识别到足够表题
- 模板类、报告类文档中的图片或表格可能只是版式元素

## manual_review_required

`manual_review_required` 仅由以下风险触发：

- `blocking`
- `high_risk`

以下风险不触发：

- `warning`
- `info`

这使真实 DOCX 回归从早期的 `10/10 manual_review_required=true` 优化为 `1/10 manual_review_required=true`，减少“所有文档都像高危”的产品误导。

## 展示原则

- `manual_review_items`：只放 blocking 和 high_risk。
- `warning_items`：放 warning。
- `info_items`：放 info。
- `risk_summary`：汇总四类风险数量。

用户界面应该把 high_risk 和 warning 分开展示，避免把普通提示包装成严重问题。
