# 课程验收记录

本记录汇总 2026-10-28 教师维护版的本地验收，参考实现、隐藏测试和教师验证命令仅在完整维护版可用。公开版由 GitHub Actions 执行公开 starter 检查。环境为 Linux x86_64、Python 3.14.6、GNU Make 4.3 和 Git 2.43。课程的运行要求和命令见 [环境指南](environment.md)。

## 实验与评分

| 实验 | 公开测试数 | 隐藏测试数 | 参考实现完整分数 |
|---|---:|---:|---:|
| 01 报文 | 20 | 11 | 100/100 |
| 02 重组 | 25 | 20 | 100/100 |
| 03 传输 | 25 | 20 | 100/100 |
| 04 转发 | 20 | 12 | 100/100 |
| 05 路由 | 20 | 10 | 100/100 |
| 06 代理 | 20 | 28 | 100/100 |
| 合计 | 130 | 101 | 600/600 |

`make grade MODE=reference SUITE=full REPORT_DIR=reports/final-reference` 在本地通过全部 231 项。`make grade PYTHON=/usr/bin/python3.12 MODE=reference SUITE=full REPORT_DIR=reports/python312-reference` 在 Python 3.12.3 下同样通过全部 231 项、600/600。`make validate` 中两次参考实现完整评分均为 600/600；公开 starter 基线分别为 0、4、4、0、0、5 分，反映留给学生实现的任务。

## 验证范围和结果

- `make build` 与 `make audit` 通过；静态审计检查六实验必需文件、18 节结构、测试权重、类别、接口参数形状、私有导入及本地文档链接。
- `make validate` 通过：12 个协议行为变异均被检出；超时、内存和导入失败的故障注入按预期失败；学生包白名单、链接、构建与公开评分基线检查通过。
- 完整验证报告和归档 SHA-256 的固定快照由维护仓库的 `evidence/validation.json` 记录；参考评分明细位于 `reports/final-reference/grade.json`。课程结构审计及代码和文档规模见维护仓库的 `evidence/course-audit.json`。
- 教师维护版验收时本地等价验证命令通过；当时尚未运行远端 CI。公开版 CI 由 GitHub Actions 执行。Docker daemon 不可用，镜像清单请求出现 TLS EOF，本次未完成 Docker 镜像构建与容器运行。容器操作命令见 [环境指南](environment.md)。

完整评分按公开 60%、隐藏 40% 合成；课程成绩与人工报告的换算见 [评分说明](grading.md)。
