# Real Document Inventory

更新时间：2026-06-01

本目录用于保存公开可下载的真实 DOCX 测试样本，供后续手动或批量回归验证使用。当前仅收集文档样本和来源清单，不运行 Agent，不修改业务代码。

## 收集原则

- 仅收集 DOCX 文件，不收集 PDF、CAJ、WPS 或网页副本。
- 优先选择高校官网、学院官网、实验中心或期刊/教务公开页面附件。
- 跳过需要登录、付费、验证码、非公开网盘或来源不清的资源。
- 样本仅用于本地格式稳定性测试；如后续需要提交真实论文正文，应先完成脱敏。

## 统计

| 指标 | 数量 |
| --- | ---: |
| 成功收集数量 | 10 |
| DOCX 数量 | 10 |
| 可用于 Agent 测试数量 | 10 |
| 需要登录/付费数量 | 0 |
| 非 DOCX 数量 | 0 |

## 文件清单

| 文件名 | 来源网址 | 文件类型 | 下载状态 | 是否适合作为测试样本 | 备注 |
| --- | --- | --- | --- | --- | --- |
| cczu_huide_science_thesis_template_2025.docx | https://hdc.cczu.edu.cn/_upload/article/files/ac/58/9a8eb71f409a91171e2bb7963c41/594be91d-a395-4872-80f9-a64edb34a731.docx | 毕业论文模板 | 成功 | 是 | 理工科毕业设计/论文模板，可测试标题、目录、图表、参考文献结构 |
| cczu_huide_econ_management_liberal_arts_thesis_template_2025.docx | https://hdc.cczu.edu.cn/_upload/article/files/ac/58/9a8eb71f409a91171e2bb7963c41/633f09e1-3d3a-4691-954b-0afa5b320ea5.docx | 毕业论文模板 | 成功 | 是 | 经管文科类毕业设计/论文模板，可测试模板差异 |
| hbue_comprehensive_simulation_lab_report_template.docx | https://etc.hbue.edu.cn/_upload/article/files/c3/00/95ff2d7b438992508358ce5cda0d/104b1c2e-e691-4e50-a82f-733a10ab2e6b.docx | 实验报告模板 | 成功 | 是 | 综合模拟实验报告，含多表格结构 |
| hbue_erp2_personal_lab_report_template.docx | https://etc.hbue.edu.cn/_upload/article/files/c3/00/95ff2d7b438992508358ce5cda0d/d527e63c-e61a-43ac-ab04-0c17eb4db764.docx | 实验报告模板 | 成功 | 是 | ERP 个人实验报告，可测试实验报告分类 |
| hbue_digital_management_team_lab_report_template.docx | https://etc.hbue.edu.cn/_upload/article/files/c3/00/95ff2d7b438992508358ce5cda0d/ef88cf54-e9c8-4988-acbe-aad8b7125c87.docx | 实验报告模板 | 成功 | 是 | 团队实验报告，表格数量较多 |
| scut_graduate_literature_review_template.docx | https://www2.scut.edu.cn/_upload/article/files/f5/7b/b7fc273040c5b378e7f4bd21f0d6/b5a1ee93-3b9e-48a8-bb74-42fa2f91033d.docx | 文献综述模板 | 成功 | 是 | 研究生培养文档，可测试参考文献与章节识别 |
| scut_graduate_proposal_report_template.docx | https://www2.scut.edu.cn/_upload/article/files/f5/7b/b7fc273040c5b378e7f4bd21f0d6/5ce1f8e2-21e5-4693-84d9-f22ab61cd5e9.docx | 开题报告模板 | 成功 | 是 | 开题报告结构，含表格，可测试非普通论文分类 |
| ecnu_course_assessment_report_template.docx | https://bksy.ecnu.edu.cn/_upload/article/files/b9/7c/0a2bc0984a12b83eff76f9731895/69a8c81d-8220-4743-be05-f267749a6290.docx | 课程/报告模板 | 成功 | 是 | 课程考核报告类表单，可测试短文档与表单结构 |
| byau_journal_paper_template.docx | https://www.byau.edu.cn/_upload/article/files/83/45/29842482445bac57cbc9993f825c/396fe003-07da-4bdf-93d9-4feb20792912.docx | 学术论文模板 | 成功 | 是 | 期刊/论文模板，含中英文摘要与参考文献区域 |
| zju_professional_practice_report_template.docx | https://psymap.zju.edu.cn/_upload/article/files/10/e7/edefaead45e38c3974cdedac467e/35d11d5e-3e30-4031-a54b-e168a1c16a52.docx | 实践报告模板 | 成功 | 是 | 专业实践报告，可测试报告类格式与章节结构 |

## DOCX 有效性检查

所有已下载文件均通过 ZIP/DOCX 结构检查，并可被 `python-docx` 打开读取。未发现 HTML 错误页伪装成 DOCX 的情况。

| 文件名 | 段落数 | 表格数 |
| --- | ---: | ---: |
| byau_journal_paper_template.docx | 178 | 2 |
| cczu_huide_econ_management_liberal_arts_thesis_template_2025.docx | 475 | 2 |
| cczu_huide_science_thesis_template_2025.docx | 473 | 2 |
| ecnu_course_assessment_report_template.docx | 3 | 1 |
| hbue_comprehensive_simulation_lab_report_template.docx | 155 | 9 |
| hbue_digital_management_team_lab_report_template.docx | 151 | 14 |
| hbue_erp2_personal_lab_report_template.docx | 74 | 2 |
| scut_graduate_literature_review_template.docx | 80 | 0 |
| scut_graduate_proposal_report_template.docx | 44 | 8 |
| zju_professional_practice_report_template.docx | 35 | 0 |

## 后续推荐来源

- 高校教务处、研究生院、学院毕业设计页面：适合继续补充毕业论文、开题报告、模板错配样本。
- 高校实验教学中心公开附件：适合继续补充实验报告和表格密集型样本。
- 学报或期刊官网投稿模板页面：适合继续补充学术论文模板和中英文摘要样本。
- 搜索建议：`site:edu.cn filetype:docx 毕业论文 模板`、`site:edu.cn filetype:docx 开题报告 模板`、`site:edu.cn filetype:docx 实验报告 模板`、`site:edu.cn filetype:docx 课程论文 模板`。
