# Regression Results

本文档整理 v0.4-beta 阶段真实 DOCX 回归结果。

## 数据来源

- 真实 DOCX 清单：`paper-ai/backend/test_documents/real/real_document_inventory.md`
- 回归 CSV：`paper-ai/backend/regression_results/summary.csv`
- 回归 JSON：`paper-ai/backend/regression_results/summary.json`

真实 DOCX 样本来自公开可下载的高校或机构附件，类型包括毕业论文模板、课程报告模板、实验报告模板、开题报告模板、文献综述模板和实践报告模板。

## 总览

| 指标 | 结果 |
| --- | ---: |
| 样本数 | 10 |
| PASS | 10 |
| FAIL | 0 |
| PASS率 | 100% |
| manual_review_required | 1/10 |
| manual_review_recommended | 1 |
| advisory_notice_only | 9 |

## 样本结果

| 文件名 | 分类 | 修改前 | 修改后 | 结果 | 复查策略 |
| --- | --- | ---: | ---: | --- | --- |
| byau_journal_paper_template.docx | 标准论文 | 73 | 85 | PASS | manual_review_recommended |
| cczu_huide_econ_management_liberal_arts_thesis_template_2025.docx | 标准论文 | 74 | 84 | PASS | advisory_notice_only |
| cczu_huide_science_thesis_template_2025.docx | 标准论文 | 77 | 84 | PASS | advisory_notice_only |
| ecnu_course_assessment_report_template.docx | 未知文档 | 73 | 73 | PASS | advisory_notice_only |
| hbue_comprehensive_simulation_lab_report_template.docx | 标准论文 | 76 | 86 | PASS | advisory_notice_only |
| hbue_digital_management_team_lab_report_template.docx | 标准论文 | 75 | 83 | PASS | advisory_notice_only |
| hbue_erp2_personal_lab_report_template.docx | 标准论文 | 77 | 86 | PASS | advisory_notice_only |
| scut_graduate_literature_review_template.docx | 标准论文 | 78 | 89 | PASS | advisory_notice_only |
| scut_graduate_proposal_report_template.docx | 标准论文 | 73 | 87 | PASS | advisory_notice_only |
| zju_professional_practice_report_template.docx | 标准论文 | 75 | 86 | PASS | advisory_notice_only |

## 风险统计

| 风险等级 | 数量 |
| --- | ---: |
| blocking | 0 |
| high_risk | 2 |
| warning | 10 |
| info | 13 |

## 主要发现

- 10 篇真实 DOCX 均能完成格式处理、报告生成、预览生成和下载验证。
- v0.3.9 Risk Level System 后，`manual_review_required` 从 10/10 降到 1/10。
- 多数真实模板触发的是 warning 或 info，例如缺参考文献章节、Word 表格无表题、模板图片无图题等。
- 唯一高风险样本集中在论文模板中的图表或参考文献编号关系，需要人工复查是合理的。
- 分类仍有边界问题：报告模板、课程模板和论文模板之间的结构相似，可能被识别为标准论文或未知文档。

## 结论

当前 v0.4-beta 可展示为稳定的 Format Agent：真实 DOCX 主流程通过率为 100%，且人工复查提示已经从“全部高危”调整为分层风险提示。

后续重点不是继续包装结果，而是增强内容级修改能力、复杂 Word 对象支持和真实修改量解释。
